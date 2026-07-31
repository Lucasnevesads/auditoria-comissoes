# Decisões do projeto

Registro do **porquê**, não do que foi feito. O código já mostra o que foi feito.

---

## 31/07/2026 · A auditoria é proibida de ler o gabarito, e a proibição é código

**Situação:** a base traz `gabarito_defeitos.csv`, que diz exatamente onde estão os 24 erros. Nada impedia a auditoria de abrir esse arquivo.

**Alternativas:** confiar na disciplina e escrever no README "não leia o gabarito", ou tornar a leitura impossível.

**Escolhi:** tornar impossível. `config/fontes.yml` lista as tabelas permitidas, o gabarito não está nela, e `fontes.carregar()` levanta `PermissionError` para quem pedir. A pontuação vive em `src/medir.py`, arquivo separado que só roda depois.

**Custo:** duas camadas a mais para uma coisa que uma linha de comentário "resolveria". Mas comentário não resolve: seis meses depois, alguém (inclusive eu) faria o join sem perceber que estava colando. Regra que depende de lembrar não é regra.

---

## 31/07/2026 · A ponte explica, não acusa

**Situação:** o jeito rápido de fazer essa auditoria seria calcular a diferença de R$ 630 mil e listar os achados.

**Alternativas:** apontar a diferença e os erros, ou decompor a diferença antes de apontar qualquer coisa.

**Escolhi:** decompor primeiro. A ponte separa a diferença em apólices canceladas, parcelas não vencidas e negócio sem lastro, e só o resíduo é tratado como problema.

O motivo é prático e é o ponto do projeto inteiro. Um relatório que diz "faltam R$ 630 mil" está **errado**, cria pânico e queima a confiança de quem o escreveu. Um que diz "R$ 444 mil ainda não venceram, R$ 138 mil foram cancelados, e R$ 48 mil o financeiro nunca registrou" resolve o problema e aponta a única coisa que exige ação.

**Custo:** a ponte precisa ser mantida. Toda regra de negócio nova (um novo status, um novo tipo de estorno) exige um componente novo, senão ele cai no resíduo e vira alarme falso. É manutenção que uma lista de erros não teria.

---

## 31/07/2026 · A primeira versão da ponte contava o mesmo dinheiro duas vezes

**Situação:** a ponte fechava com um resíduo de -R$ 1.672,06, que eu quase publiquei como "achado interessante".

**Alternativas:** tratar o resíduo como sinal do defeito, ou investigar de onde ele vinha.

**Escolhi:** investigar. O resíduo era bug meu: as parcelas de apólice cancelada que ficaram marcadas como "Pendente" entravam em **dois** componentes ao mesmo tempo, o de canceladas e o de pendentes, e a ponte subtraía o mesmo dinheiro duas vezes. Com o filtro correto o resíduo caiu para -R$ 0,65, que é a soma real das divergências de centavos.

**Custo:** nenhum, e por isso o registro fica. O que quase aconteceu foi pior que o bug: eu ia contar uma história bonita ("olha, o resíduo aponta exatamente para o defeito") em cima de um erro de conta. Resíduo que "coincidentemente" bate com um achado quase sempre é dupla contagem, não descoberta.

---

## 31/07/2026 · Casar as bases pelo par (apólice, parcela), não por id

**Situação:** seria mais simples se a planilha do financeiro tivesse o id da parcela.

**Alternativas:** pedir que a base exporte o id na planilha, ou casar pelo que a planilha realmente tem.

**Escolhi:** casar por `numero_apolice` + `numero_parcela`. Planilha de produção é digitada a partir do documento e não guarda id de sistema. Aliás, foi ao escrever esta auditoria que percebi que a base estava exportando o id, e o projeto da base foi corrigido por causa disso.

**Custo:** o join fica sujeito a erro de digitação no número da apólice, e uma linha mal digitada some da conferência em silêncio. É exatamente o risco que existe na vida real, então o custo é o realismo funcionando. A conferência `numero_de_apolice_repetido` existe para cobrir o outro lado desse mesmo risco.

---

## 31/07/2026 · Uma conferência que sempre passa

**Situação:** `numero_de_apolice_repetido` acha zero e vai continuar achando zero enquanto a base for gerada como é.

**Alternativas:** tirar do código por não achar nada, ou manter.

**Escolhi:** manter. Se dois contratos tiverem o mesmo número, **todas** as outras conferências passam a errar em silêncio, porque o casamento entre as bases depende desse número. O valor dela não é o que ela acha, é o que ela garante.

**Custo:** o relatório mostra uma linha com zero, o que parece desperdício para quem lê rápido. Preferível a descobrir seis meses depois que a auditoria inteira estava errada e ninguém tinha como saber.
