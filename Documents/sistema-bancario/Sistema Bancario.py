import json
from datetime import datetime
import os

ARQUIVO_DADOS = "banco_dados.json"
LIMITE_SAQUE = 500
LIMITE_SAQUES_DIARIOS = 3


# ==============================
# CLASSES PRINCIPAIS
# ==============================

class Cliente:
    def __init__(self, nome, cpf, data_nascimento, endereco):
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento
        self.endereco = endereco
        self.contas = []

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class ContaCorrente:
    def __init__(self, agencia, numero_conta, cliente):
        self.agencia = agencia
        self.numero_conta = numero_conta
        self.cliente = cliente
        self.saldo = 0.0
        self.extrato = []
        self.numero_saques = 0

    def registrar_operacao(self, tipo, valor):
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.extrato.append(f"{data_hora} - {tipo}: R$ {valor:.2f}")

    def depositar(self, valor):
        if valor <= 0:
            print("⚠️ Valor inválido.")
            return False
        self.saldo += valor
        self.registrar_operacao("Depósito", valor)
        print(f"✅ Depósito de R$ {valor:.2f} realizado com sucesso!")
        return True

    def sacar(self, valor):
        if valor <= 0:
            print("⚠️ Valor inválido.")
            return False
        elif valor > self.saldo:
            print("❌ Saldo insuficiente.")
            return False
        elif valor > LIMITE_SAQUE:
            print(f"❌ Valor excede o limite de R$ {LIMITE_SAQUE:.2f}.")
            return False
        elif self.numero_saques >= LIMITE_SAQUES_DIARIOS:
            print("❌ Número máximo de saques diários atingido.")
            return False
        else:
            self.saldo -= valor
            self.numero_saques += 1
            self.registrar_operacao("Saque", valor)
            print(f"✅ Saque de R$ {valor:.2f} realizado com sucesso!")
            return True

    def exibir_extrato(self):
        print("\n================ EXTRATO ================")
        if not self.extrato:
            print("Não foram realizadas movimentações.")
        else:
            for linha in self.extrato:
                print(linha)
        print(f"\nSaldo atual: R$ {self.saldo:.2f}")
        print("=========================================")


# ==============================
# CLASSE BANCO
# ==============================

class Banco:
    def __init__(self):
        self.dados = self.carregar_dados()
        self.usuarios = self.dados.get("usuarios", [])
        self.contas = self.dados.get("contas", [])

    # ---------- Persistência ----------
    def salvar_dados(self):
        dados = {"usuarios": self.usuarios, "contas": self.contas}
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, indent=4, ensure_ascii=False)

    def carregar_dados(self):
        if os.path.exists(ARQUIVO_DADOS):
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        else:
            return {"usuarios": [], "contas": []}

    # ---------- Usuários ----------
    def buscar_usuario(self, cpf):
        for u in self.usuarios:
            if u["cpf"] == cpf:
                return u
        return None

    def criar_usuario(self):
        cpf = input("Informe o CPF (somente números): ")
        if self.buscar_usuario(cpf):
            print("❌ Já existe um usuário com esse CPF!")
            return

        nome = input("Nome completo: ")
        data_nascimento = input("Data de nascimento (dd/mm/aaaa): ")
        endereco = input("Endereço (logradouro, nº - bairro - cidade/sigla estado): ")

        novo_usuario = {
            "nome": nome,
            "cpf": cpf,
            "data_nascimento": data_nascimento,
            "endereco": endereco
        }
        self.usuarios.append(novo_usuario)
        self.salvar_dados()
        print(f"✅ Usuário {nome} cadastrado com sucesso!")

    # ---------- Contas ----------
    def criar_conta(self, agencia="0001"):
        cpf = input("Informe o CPF do titular: ")
        usuario = self.buscar_usuario(cpf)

        if not usuario:
            print("❌ Usuário não encontrado! Cadastre primeiro o usuário.")
            return

        numero_conta = len(self.contas) + 1
        nova_conta = {
            "agencia": agencia,
            "numero_conta": numero_conta,
            "cpf": cpf,
            "saldo": 0.0,
            "extrato": [],
            "numero_saques": 0
        }
        self.contas.append(nova_conta)
        self.salvar_dados()
        print(f"✅ Conta criada! Agência: {agencia} | Conta: {numero_conta}")

    def listar_contas(self):
        if not self.contas:
            print("⚠️ Nenhuma conta cadastrada.")
            return

        for conta in self.contas:
            usuario = self.buscar_usuario(conta["cpf"])
            print(f"""
Agência: {conta['agencia']}
Conta: {conta['numero_conta']}
Titular: {usuario['nome']}
Saldo: R$ {conta['saldo']:.2f}
-----------------------------
""")

    # ---------- Login ----------
    def login(self):
        cpf = input("Informe seu CPF: ")
        contas_usuario = [c for c in self.contas if c["cpf"] == cpf]

        if not contas_usuario:
            print("❌ Nenhuma conta encontrada para este CPF.")
            return None

        print("Contas disponíveis:")
        for conta in contas_usuario:
            print(f"Agência: {conta['agencia']} | Conta: {conta['numero_conta']}")

        try:
            numero = int(input("Informe o número da conta que deseja acessar: "))
            conta_dados = next((c for c in contas_usuario if c["numero_conta"] == numero), None)
            if conta_dados:
                usuario = self.buscar_usuario(cpf)
                conta = ContaCorrente(conta_dados["agencia"], conta_dados["numero_conta"], usuario)
                conta.saldo = conta_dados["saldo"]
                conta.extrato = conta_dados["extrato"]
                conta.numero_saques = conta_dados["numero_saques"]
                print(f"✅ Login bem-sucedido! Bem-vindo, {usuario['nome']}!")
                return conta
            else:
                print("⚠️ Conta não encontrada.")
                return None
        except ValueError:
            print("⚠️ Número de conta inválido.")
            return None

    # ---------- Atualiza dados após movimentação ----------
    def atualizar_conta(self, conta):
        for c in self.contas:
            if c["agencia"] == conta.agencia and c["numero_conta"] == conta.numero_conta:
                c["saldo"] = conta.saldo
                c["extrato"] = conta.extrato
                c["numero_saques"] = conta.numero_saques
                self.salvar_dados()
                break


# ==============================
# MENUS
# ==============================

def menu_principal():
    print("""
============ MENU PRINCIPAL ============
[1] Criar usuário
[2] Criar conta
[3] Listar contas
[4] Acessar conta
[q] Sair
========================================
""")


def menu_conta():
    print("""
============ CONTA CORRENTE ============
[1] Depositar
[2] Sacar
[3] Extrato
[0] Voltar
========================================
""")


# ==============================
# EXECUÇÃO PRINCIPAL
# ==============================

def main():
    banco = Banco()

    while True:
        menu_principal()
        opcao = input("Escolha uma opção: ").lower()

        if opcao == "1":
            banco.criar_usuario()
        elif opcao == "2":
            banco.criar_conta()
        elif opcao == "3":
            banco.listar_contas()
        elif opcao == "4":
            conta = banco.login()
            if conta:
                while True:
                    menu_conta()
                    escolha = input("Escolha uma operação: ").lower()
                    if escolha == "1":
                        try:
                            valor = float(input("Valor do depósito: "))
                            if conta.depositar(valor):
                                banco.atualizar_conta(conta)
                        except ValueError:
                            print("⚠️ Valor inválido.")
                    elif escolha == "2":
                        try:
                            valor = float(input("Valor do saque: "))
                            if conta.sacar(valor):
                                banco.atualizar_conta(conta)
                        except ValueError:
                            print("⚠️ Valor inválido.")
                    elif escolha == "3":
                        conta.exibir_extrato()
                    elif escolha == "0":
                        print("👋 Retornando ao menu principal...")
                        break
                    else:
                        print("⚠️ Opção inválida.")
        elif opcao == "q":
            print("👋 Encerrando o sistema bancário. Até logo!")
            break
        else:
            print("⚠️ Opção inválida.")


if __name__ == "__main__":
    main()
