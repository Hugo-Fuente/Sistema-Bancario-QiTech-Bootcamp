from fastapi import FastAPI

from constants import check_variables
from errors import register_error_handlers
from errors.base_error import error_verification
from middlewares import (
    register_internal_token_middleware,
    register_request_context_middleware,
    register_request_logger_middleware,
    register_session_manager_middleware,
)
from resources import (
    ContaResource,
    EmpresaResource,
    HealthCheckResource,
    PagamentoProgramadoResource,
    ResponsabilidadeResource,
    TransacaoResource,
)
from utils.logger import setup_logging


def create_app() -> FastAPI:
    """Monta a aplicação, peça por peça.

    Os três blocos abaixo seguem a ordem em que a requisição encontra
    cada um — de fora pra dentro:
      1. os middlewares    — o que acontece com TODA requisição
      2. as rotas          — o que a API sabe responder
      3. os error handlers — como cada erro vira uma resposta

    Essa ordem serve pra leitura, não é exigência: o FastAPI monta a
    pilha de middlewares na primeira requisição que chega, então
    registrar rota antes ou depois de middleware dá no mesmo. Só a
    ordem DENTRO do bloco de middlewares tem consequência, e ela está
    explicada logo abaixo.
    """
    # Os três None desligam a documentação automática: o FastAPI sabe
    # gerar sozinho umas páginas descrevendo a API, e aqui elas não
    # existem. Pra ver o que cada rota responde, mande uma requisição —
    # tem exemplo pronto de cada uma no README.

    application = FastAPI(
        title="Sistema Bancário API",
        description="API do Bootcamp QiTech"
    )

#    application = FastAPI(
#        docs_url=None,
#        redoc_url=None,
#        openapi_url=None,
#    )

    # ────────────────────────────────────────────────────────────────
    # Os middlewares — e a ordem deles, que é regra e não gosto
    # ────────────────────────────────────────────────────────────────
    # Middleware é uma camada por fora da aplicação: toda requisição
    # atravessa todas elas na ida, e todas de novo na volta. São como
    # cascas de cebola, e o ÚLTIMO registrado é a casca de FORA.
    #
    # Ou seja: destas quatro linhas, a de BAIXO é a primeira que a
    # requisição encontra, e a de CIMA é a última. Lendo de fora para
    # dentro, acontece isto:
    #
    #     requisição chega
    #           ↓
    #     request_context   dá um identificador único a esta requisição
    #           ↓
    #     request_logger    escreve "ENTROU" e, na volta, "SAIU"
    #           ↓
    #     internal_token    confere o INTERNAL-TOKEN. Sem ele, para aqui
    #           ↓
    #     session_manager   cuida da sessão de banco: desfaz se deu
    #           ↓           errado, fecha sempre — e nunca salva
    #           ↓
    #     as rotas
    #
    # Cada posição tem um porquê, e trocar duas linhas muda o que a API
    # faz:
    #
    # • O identificador vem ANTES do log: se viesse depois, as linhas de
    #   log da requisição sairiam sem o nome dela, e o middleware
    #   existiria para nada.
    # • O log vem ANTES do token: assim a tentativa recusada com 403
    #   também aparece no log — e essa é justamente a que você quer ver,
    #   porque mil delas seguidas é alguém tentando adivinhar o token.
    # • A sessão de banco fica por DENTRO do token, encostada nas
    #   rotas: quem não passou na porta leva 403 na camada de cima e não
    #   chega a ter uma sessão. É o mais interno de propósito — banco é
    #   o recurso mais caro desta lista, e o último que se empresta.
    #
    # Nada disso é teoria, e dá pra ver com os olhos. Troque as duas
    # últimas linhas de lugar (o identificador passa a ser registrado
    # antes do log, ou seja, a executar DEPOIS dele), chame qualquer
    # rota e olhe o log:
    #
    #     docker compose logs api | grep request_logger | tail -2
    #
    # (O grep é necessário: sem ele o tail pega a linha de acesso do
    # uvicorn, que é outra coisa e não passa por este middleware.)
    #
    # As duas linhas saem com [-] no lugar do identificador: o log
    # aconteceu antes de existir um nome para aquela requisição. Desfaça
    # a troca e o nome volta.
    #
    # Repare no que essa experiência tem de incômodo: a suíte continua
    # TODA VERDE com a ordem trocada. Nenhum teste aqui guarda esta
    # ordem — o preço aparece no dia do incidente, quando o log não
    # servir pra achar a requisição. Teste que não existe não avisa
    # nada, e é por isso que este comentário existe.
    #
    # ATENÇÃO, e é aqui que quase todo mundo tropeça: as quatro linhas
    # abaixo são o DIAGRAMA ACIMA DE TRÁS PRA FRENTE. O FastAPI embrulha
    # a aplicação de dentro pra fora, então o ÚLTIMO registrado é o
    # PRIMEIRO a executar. Leia de baixo pra cima e o diagrama volta.
    register_session_manager_middleware(application)
    register_internal_token_middleware(application)
    register_request_logger_middleware(application)
    register_request_context_middleware(application)

    # ────────────────────────────────────────────────────────────────
    # As rotas — o endereço, o verbo, e quem atende
    # ────────────────────────────────────────────────────────────────
    # Cada linha liga um endereço a um método de um resource. É a lista
    # COMPLETA do que esta API atende: rota que não está aqui não
    # existe, e não há um segundo lugar para procurar.
    #
    # Nos serviços da QI o framework é o Falcon, que descobre o método
    # pelo nome — chegou um POST, ele procura um `on_post`, e o registro
    # é uma linha por ENDEREÇO. O FastAPI não faz essa descoberta, então
    # aqui é uma linha por endereço E verbo. Custa mais linhas; em troca,
    # não existe rota que atenda sem estar escrita nesta lista.
    #
    # Repare no que NÃO está escrito aqui: o status de cada resposta.
    # 201, 202, 204 — todos saem de dentro do resource, que é quem sabe
    # se a coisa foi criada, agendada ou concluída. Esta lista diz QUEM
    # atende cada endereço, e mais nada.
    health_check_resource = HealthCheckResource()
    empresa_resource = EmpresaResource()
    conta_resource = ContaResource()
    transacao_resource = TransacaoResource()
    responsabilidade_resource = ResponsabilidadeResource()
    pagamento_resource = PagamentoProgramadoResource()

    # A tabela de endereços: QUEM atende cada rota. Caminhos no singular, como
    # no base-service; ações sobre um recurso são sub-recursos (/aprovacao,
    # /cancelamento, /execucao). Status e regra de negócio moram nas camadas
    # de baixo — aqui só o mapa.
    routes = [
        ("/", health_check_resource.on_get_home, ["GET"]),
        ("/health_check", health_check_resource.on_get_health_check, ["GET"]),
        # empresa, sócios, governança
        ("/empresa", empresa_resource.on_post, ["POST"]),
        ("/empresa/{empresa_id}", empresa_resource.on_get, ["GET"]),
        ("/empresa/{empresa_id}/socio/{empresa_socio_id}/permissao/{acao}", empresa_resource.on_put_permissao, ["PUT"]),
        ("/empresa/{empresa_id}/socio/{empresa_socio_id}/permissao/{acao}", empresa_resource.on_delete_permissao, ["DELETE"]),
        ("/empresa/{empresa_id}/regra_aprovacao", empresa_resource.on_put_regra, ["PUT"]),
        ("/empresa/{empresa_id}/regra_aprovacao/{regra_id}", empresa_resource.on_delete_regra, ["DELETE"]),
        # conta
        ("/conta/{conta_id}", conta_resource.on_get, ["GET"]),
        ("/conta/{conta_id}/status", conta_resource.on_patch_status, ["PATCH"]),
        ("/conta/{conta_id}/extrato", conta_resource.on_get_extrato, ["GET"]),
        ("/conta/{conta_id}/pagamento_programado", conta_resource.on_get_pagamentos, ["GET"]),
        # responsabilidade, substituição, orçamento, reserva
        ("/responsabilidade", responsabilidade_resource.on_post, ["POST"]),
        ("/responsabilidade/{responsabilidade_id}", responsabilidade_resource.on_get, ["GET"]),
        ("/responsabilidade/{responsabilidade_id}/substituicao", responsabilidade_resource.on_put_substituicao, ["PUT"]),
        ("/responsabilidade/{responsabilidade_id}/orcamento/{competencia}", responsabilidade_resource.on_put_orcamento, ["PUT"]),
        ("/movimento_reserva", responsabilidade_resource.on_post_movimento, ["POST"]),
        ("/movimento_reserva/{movimento_id}/aprovacao", pagamento_resource.on_post_aprovacao_movimento, ["POST"]),
        # transação
        ("/transacao", transacao_resource.on_post, ["POST"]),
        ("/transacao/{transacao_id}", transacao_resource.on_get, ["GET"]),
        # pagamento programado
        ("/pagamento_programado", pagamento_resource.on_post, ["POST"]),
        ("/pagamento_programado/{pagamento_id}/aprovacao", pagamento_resource.on_post_aprovacao, ["POST"]),
        ("/pagamento_programado/{pagamento_id}/cancelamento", pagamento_resource.on_post_cancelamento, ["POST"]),
        ("/pagamento_programado/{pagamento_id}/execucao", pagamento_resource.on_post_execucao, ["POST"]),
    ]

    for path, endpoint, methods in routes:
        application.add_api_route(path, endpoint, methods=methods)

    register_error_handlers(application)

    return application


def main() -> FastAPI:
    # Não deixa a API subir com configuração faltando: é melhor falhar
    # agora, na hora de ligar, do que na cara do cliente mais tarde.
    check_variables()
    error_verification()
    setup_logging()

    return create_app()


app = main()
