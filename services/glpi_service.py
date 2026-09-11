# services/glpi_service.py
"""
Serviço enxuto de leitura do GLPI, usado só pelo poller de notificação
por email. Não cria chamados — apenas lê tickets novos e descobre o
requerente de cada um.
"""

import re
import requests
from config import settings, logger

# Mapa de status do GLPI (core) -> texto exibido
TICKET_STATUS_MAP = {
    1: "Novo",
    2: "Em atendimento (atribuído)",
    3: "Em atendimento (planejado)",
    4: "Pendente",
    5: "Solucionado",
    6: "Fechado",
}


class GLPIService:
    def __init__(self):
        self.url = settings.GLPI_URL.rstrip('/')
        self.app_token = settings.GLPI_APP_TOKEN
        self.user_token = settings.GLPI_USER_TOKEN

    # -----------------------------------------------------------------
    # Sessão
    # -----------------------------------------------------------------
    def get_session_headers(self) -> dict | None:
        """Abre uma sessão no GLPI e retorna os headers prontos para uso."""
        headers = {
            "Content-Type": "application/json",
            "App-Token": self.app_token,
            "Authorization": f"user_token {self.user_token}",
        }
        try:
            res = requests.post(f"{self.url}/initSession", headers=headers, timeout=10)
            if res.status_code == 200:
                session_token = res.json().get("session_token")
                return {
                    "Content-Type": "application/json",
                    "App-Token": self.app_token,
                    "Session-Token": session_token,
                }
            logger.error(f"Erro ao iniciar sessão GLPI: Status {res.status_code} - {res.text}")
            return None
        except Exception as e:
            logger.exception(f"Exceção na autenticação com GLPI: {e}")
            return None

    def kill_session(self, headers: dict) -> None:
        try:
            requests.get(f"{self.url}/killSession", headers=headers, timeout=5)
        except Exception as e:
            logger.warning(f"Erro ao fechar sessão GLPI: {e}")

    # -----------------------------------------------------------------
    # Paginação - busca TODOS os tickets
    # -----------------------------------------------------------------
    def _fetch_all_ticket_ids(self, headers: dict) -> list[int]:
        """Percorre /Ticket em páginas até esgotar o total."""
        page_size = settings.GLPI_FETCH_PAGE_SIZE
        ids = []
        start = 0
        safety_cap = 20000

        while True:
            end = start + page_size - 1
            try:
                res = requests.get(
                    f"{self.url}/Ticket",
                    headers=headers,
                    params={"range": f"{start}-{end}", "expand_dropdowns": "false"},
                    timeout=20,
                )
            except Exception as e:
                logger.exception(f"Erro ao paginar tickets (range {start}-{end}): {e}")
                break

            if res.status_code not in (200, 206):
                logger.error(f"Erro ao listar tickets (range {start}-{end}): Status {res.status_code}")
                break

            batch = res.json()
            if not isinstance(batch, list):
                batch = [batch]

            if not batch:
                break

            ids.extend(int(t["id"]) for t in batch if isinstance(t, dict) and "id" in t)

            content_range = res.headers.get("Content-Range", "")
            total = None
            if content_range and "/" in content_range:
                try:
                    total = int(content_range.split("/")[-1])
                except ValueError:
                    total = None

            start += page_size

            if total is not None and start >= total:
                break
            if len(batch) < page_size:
                break
            if start > safety_cap:
                logger.warning(f"⚠️ Trava de segurança atingida ({safety_cap})")
                break

        return ids

    # -----------------------------------------------------------------
    # Tickets novos
    # -----------------------------------------------------------------
    def get_new_tickets(self, last_id: int, headers: dict) -> list[dict]:
        """Busca tickets com id > last_id, em ordem crescente."""
        try:
            all_ids = self._fetch_all_ticket_ids(headers)
            novos_ids = sorted(i for i in all_ids if i > last_id)

            if not novos_ids:
                return []

            tickets = []
            for tid in novos_ids:
                detail = self._get_ticket_detail(tid, headers)
                if detail:
                    tickets.append(detail)

            return tickets

        except Exception as e:
            logger.exception(f"Erro ao buscar tickets novos: {e}")
            return []

    def _get_ticket_detail(self, ticket_id: int, headers: dict) -> dict | None:
        try:
            res = requests.get(f"{self.url}/Ticket/{ticket_id}", headers=headers, timeout=10)
            if res.status_code == 200:
                return res.json()
            logger.warning(f"Erro ao buscar detalhes do ticket {ticket_id}: {res.status_code}")
            return None
        except Exception as e:
            logger.warning(f"Erro ao buscar detalhes do ticket {ticket_id}: {e}")
            return None

    def get_latest_ticket_id(self, headers: dict) -> int:
        """Usado na primeira execução para saber de onde começar."""
        all_ids = self._fetch_all_ticket_ids(headers)
        return max(all_ids) if all_ids else 0

    def get_ticket_status_label(self, status_code) -> str:
        """Converte o código numérico de status em texto legível."""
        try:
            return TICKET_STATUS_MAP.get(int(status_code), f"Status #{status_code}")
        except (TypeError, ValueError):
            return "Desconhecido"

    def get_ticket_assigned(self, ticket_id: int, headers: dict) -> str:
        """Descobre quem está atribuído ao ticket."""
        # Tenta grupo atribuído
        try:
            res = requests.get(f"{self.url}/Ticket/{ticket_id}/Group_Ticket", headers=headers, timeout=10)
            if res.status_code in (200, 206):
                groups = res.json()
                if not isinstance(groups, list):
                    groups = [groups]
                for g in groups:
                    if isinstance(g, dict) and g.get("type") == 2:
                        group_id = g.get("groups_id")
                        if group_id:
                            res_group = requests.get(f"{self.url}/Group/{group_id}", headers=headers, timeout=10)
                            if res_group.status_code == 200:
                                group_name = res_group.json().get("name")
                                if group_name:
                                    return group_name
        except Exception as e:
            logger.warning(f"Erro ao buscar grupo atribuído: {e}")

        # Tenta técnico individual
        try:
            res = requests.get(f"{self.url}/Ticket/{ticket_id}/Ticket_User", headers=headers, timeout=10)
            if res.status_code in (200, 206):
                actors = res.json()
                if not isinstance(actors, list):
                    actors = [actors]
                for actor in actors:
                    if isinstance(actor, dict) and actor.get("type") == 2:
                        user_id = actor.get("users_id")
                        if user_id:
                            name, _ = self._get_user_name_and_email(user_id, headers)
                            return name
        except Exception as e:
            logger.warning(f"Erro ao buscar técnico atribuído: {e}")

        return "Não atribuído"

    # -----------------------------------------------------------------
    # CORRIGIDO: Busca documentos do ticket via API
    # -----------------------------------------------------------------
    def get_ticket_documents(self, ticket_id: int, headers: dict) -> list[tuple[str, bytes]]:
        """
        Busca todos os documentos anexados a um ticket via API Document_Item.
        Retorna lista de (filename, bytes)
        """
        documents = []
        
        try:
            # Endpoint correto: Ticket/{id}/Document_Item
            res = requests.get(
                f"{self.url}/Ticket/{ticket_id}/Document_Item",
                headers=headers,
                timeout=10
            )
            
            if res.status_code in (200, 206):
                items = res.json()
                if not isinstance(items, list):
                    items = [items]
                
                logger.info(f"📎 Encontrados {len(items)} documentos vinculados ao ticket #{ticket_id}")
                
                for item in items:
                    if isinstance(item, dict):
                        doc_id = None
                        
                        # Busca o ID do documento no link (CORREÇÃO AQUI)
                        links = item.get('links', [])
                        for link in links:
                            if link.get('rel') == 'Document':
                                href = link.get('href', '')
                                match = re.search(r'/Document/(\d+)', href)
                                if match:
                                    doc_id = int(match.group(1))
                                    logger.info(f"🔍 Documento ID {doc_id} encontrado no link: {href}")
                                    break
                        
                        # Fallback: tenta o campo documents_id se for número
                        if not doc_id:
                            doc_id_val = item.get('documents_id')
                            if doc_id_val and str(doc_id_val).isdigit():
                                doc_id = int(doc_id_val)
                                logger.info(f"🔍 Documento ID {doc_id} encontrado no campo documents_id")
                        
                        if doc_id:
                            logger.info(f"📥 Baixando documento #{doc_id}...")
                            result = self.get_document_file(doc_id, headers)
                            if result:
                                documents.append(result)
                                logger.info(f"✅ Documento #{doc_id} baixado: {result[0]}")
                        else:
                            logger.warning(f"⚠️ Não foi possível extrair ID do documento: {item}")
            else:
                logger.warning(f"Erro ao buscar documentos do ticket {ticket_id}: Status {res.status_code}")
                
        except Exception as e:
            logger.exception(f"Erro ao buscar documentos do ticket {ticket_id}: {e}")
        
        return documents

    def get_document_file(self, doc_id: int, headers: dict) -> tuple[str, bytes] | None:
        """
        Baixa o conteúdo binário de um documento/anexo do GLPI.
        Retorna (nome_do_arquivo, bytes) ou None se falhar.
        """
        try:
            dl_headers = dict(headers)
            dl_headers["Accept"] = "application/octet-stream"

            res = requests.get(
                f"{self.url}/Document/{doc_id}",
                headers=dl_headers,
                timeout=30
            )

            if res.status_code != 200:
                logger.warning(f"Erro ao baixar documento {doc_id}: Status {res.status_code}")
                return None

            if len(res.content) == 0:
                logger.warning(f"⚠️ Documento {doc_id} está vazio (0 bytes), tentando alt=media...")
                res2 = requests.get(
                    f"{self.url}/Document/{doc_id}",
                    headers=dl_headers,
                    params={"alt": "media"},
                    timeout=30
                )
                if res2.status_code == 200 and len(res2.content) > 0:
                    res = res2
                else:
                    return None

            filename = f"anexo_{doc_id}"
            content_disposition = res.headers.get("Content-Disposition", "")
            if "filename=" in content_disposition:
                match = re.search(r'filename[=*]?\s*["\']?([^"\';]+)["\']?', content_disposition)
                if match:
                    filename = match.group(1).strip().strip('"\'')

            logger.info(f"✅ Documento {doc_id} baixado: {filename} ({len(res.content)} bytes)")
            return filename, res.content

        except Exception as e:
            logger.exception(f"Erro ao baixar documento {doc_id}: {e}")
            return None

    # -----------------------------------------------------------------
    # Requerente do ticket
    # -----------------------------------------------------------------
    def get_ticket_requester(self, ticket_id: int, headers: dict) -> tuple[str, str]:
        """Retorna (nome, email) do requerente (ator tipo 1)."""
        try:
            res = requests.get(f"{self.url}/Ticket/{ticket_id}/Ticket_User", headers=headers, timeout=10)
            if res.status_code not in (200, 206):
                logger.warning(f"Erro ao buscar atores do ticket {ticket_id}: {res.status_code}")
                return "Não identificado", ""

            actors = res.json()
            if not isinstance(actors, list):
                actors = [actors]

            requester_user_id = None
            for actor in actors:
                if isinstance(actor, dict) and actor.get("type") == 1:
                    requester_user_id = actor.get("users_id")
                    break

            if not requester_user_id:
                return "Não identificado", ""

            return self._get_user_name_and_email(requester_user_id, headers)

        except Exception as e:
            logger.exception(f"Erro ao identificar requerente do ticket {ticket_id}: {e}")
            return "Não identificado", ""

    def _get_user_name_and_email(self, user_id: int, headers: dict) -> tuple[str, str]:
        name = f"Usuário #{user_id}"
        email = ""

        try:
            res_user = requests.get(f"{self.url}/User/{user_id}", headers=headers, timeout=10)
            if res_user.status_code == 200:
                user_data = res_user.json()
                firstname = user_data.get("firstname") or ""
                realname = user_data.get("realname") or ""
                full_name = f"{firstname} {realname}".strip()
                if full_name:
                    name = full_name
                elif user_data.get("name"):
                    name = user_data.get("name")
        except Exception as e:
            logger.warning(f"Erro ao buscar dados do usuário {user_id}: {e}")

        try:
            res_email = requests.get(
                f"{self.url}/User/{user_id}/UserEmail",
                headers=headers,
                params={"range": "0-1"},
                timeout=10,
            )
            if res_email.status_code in (200, 206):
                email_data = res_email.json()
                if not isinstance(email_data, list):
                    email_data = [email_data]
                if email_data and isinstance(email_data[0], dict):
                    email = email_data[0].get("email", "")
        except Exception as e:
            logger.warning(f"Erro ao buscar email do usuário {user_id}: {e}")

        return name, email