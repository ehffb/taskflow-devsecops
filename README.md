Shift-Left - é um conceito que na esteira de produção de uma aplicação, é colocada a segurança de uma aplicação desde do inicio da esteira, realizando testes e práticas de segurança.

Vulnerabilidade observada no TaskFlow: SQL Injection
no arquivo app.py, nos campos de login e senha que o usuario digita para rota de login, o codigo concatena os dados com ( + ) e quando montado para a consulta no banco de dados. Isto faz com que um atacante possa injetar codigos que o banco de dados entenda como correto( as credenciais colocadas) e liberem o acesso.
O correto e utilizar parametros preparados ( Placeholders )

Esperar o termino do desenvolvimento do software para pensar em segurança é arriscado, pois corrigir falhas de segurança quando se esta no final do projeto é muito mais caro e irá ter o retrabalho. E como as equipes tem prazos para entrega do software, evitar isto é importante.