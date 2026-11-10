import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class GerenciadorLivros(QMainWindow):

    def livro_duplicado(
        self,
        titulo,
        autor,
        isbn,
        ignorar_id=None,
    ):
        for livro in self.livros:
            # Na atualização, ignora o próprio registro
            if livro["id"] == ignorar_id:
                continue

            mesmo_titulo_autor = (
                livro["titulo"].strip().casefold()
                == titulo.strip().casefold()
                and livro["autor"].strip().casefold()
                == autor.strip().casefold()
            )

            mesmo_isbn = (
                isbn != ""
                and livro["isbn"] != ""
                and livro["isbn"].strip().casefold()
                == isbn.strip().casefold()
            )

            if mesmo_titulo_autor or mesmo_isbn:
                return True

        return False

    def __init__(self):
        super().__init__()

        # Lista que armazena os livros em memória
        self.livros = []

        # Controla o próximo ID
        self.proximo_id = 1

        # Guarda o ID do livro selecionado
        self.id_selecionado = None

        self.setWindowTitle("Gerenciador de Livros")
        self.resize(900, 900)

        self.criar_interface()
        self.aplicar_estilo()
        self.atualizar_estado_botoes()

        

    def criar_interface(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(25, 20, 25, 20)
        layout_principal.setSpacing(15)

        widget_central.setLayout(layout_principal)

        # Título da janela
        titulo_pagina = QLabel("Gerenciador de Livros")
        titulo_pagina.setObjectName("tituloPagina")
        layout_principal.addWidget(titulo_pagina)

        subtitulo = QLabel(
            "Cadastre, pesquise e organize os livros da biblioteca."
        )
        subtitulo.setObjectName("subtitulo")
        layout_principal.addWidget(subtitulo)

        # Área do formulário
        formulario = QFormLayout()
        formulario.setHorizontalSpacing(15)
        formulario.setVerticalSpacing(12)

        self.campo_titulo = QLineEdit()
        self.campo_titulo.setPlaceholderText("Digite o título do livro")

        self.campo_autor = QLineEdit()
        self.campo_autor.setPlaceholderText("Digite o nome do autor")

        self.campo_ano = QLineEdit()
        self.campo_ano.setPlaceholderText("Exemplo: 2026")
        self.campo_ano.setValidator(QIntValidator(0, 9999))
        self.campo_ano.setMaxLength(4)

        self.campo_isbn = QLineEdit()
        self.campo_isbn.setPlaceholderText("Digite o ISBN")

        formulario.addRow("Título:", self.campo_titulo)
        formulario.addRow("Autor:", self.campo_autor)
        formulario.addRow("Ano:", self.campo_ano)
        formulario.addRow("ISBN:", self.campo_isbn)

        layout_principal.addLayout(formulario)

        # Área de pesquisa
        layout_pesquisa = QHBoxLayout()

        self.campo_pesquisa = QLineEdit()
        self.campo_pesquisa.setPlaceholderText(
            "Pesquisar por título ou autor"
        )

        self.botao_pesquisar = QPushButton("Pesquisar")
        self.botao_mostrar_todos = QPushButton("Mostrar todos")

        layout_pesquisa.addWidget(self.campo_pesquisa)
        layout_pesquisa.addWidget(self.botao_pesquisar)
        layout_pesquisa.addWidget(self.botao_mostrar_todos)

        layout_principal.addLayout(layout_pesquisa)

        # Área inferior com tabela e botões
        layout_conteudo = QHBoxLayout()
        layout_conteudo.setSpacing(15)

        # Tabela
        self.tabela = QTableWidget()

        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(
            ["ID", "Título", "Autor", "Ano", "ISBN"]
        )

        self.tabela.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.tabela.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.tabela.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setVisible(False)

        cabecalho = self.tabela.horizontalHeader()

        cabecalho.setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )

        cabecalho.setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )

        cabecalho.setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )

        cabecalho.setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )

        cabecalho.setSectionResizeMode(
            4, QHeaderView.ResizeMode.Stretch
        )

        layout_conteudo.addWidget(self.tabela, 1)

        # Botões à direita
        layout_botoes = QVBoxLayout()

        self.botao_cadastrar = QPushButton("Cadastrar")
        self.botao_atualizar = QPushButton("Atualizar selecionado")
        self.botao_excluir = QPushButton("Excluir selecionado")
        self.botao_limpar = QPushButton("Limpar")
        self.botao_fechar = QPushButton("Fechar")

        self.botao_cadastrar.setObjectName("botaoCadastrar")
        self.botao_atualizar.setObjectName("botaoAtualizar")
        self.botao_excluir.setObjectName("botaoExcluir")
        self.botao_limpar.setObjectName("botaoLimpar")
        self.botao_fechar.setObjectName("botaoFechar")

        layout_botoes.addWidget(self.botao_cadastrar)
        layout_botoes.addWidget(self.botao_atualizar)
        layout_botoes.addWidget(self.botao_excluir)
        layout_botoes.addWidget(self.botao_limpar)
        layout_botoes.addStretch()
        layout_botoes.addWidget(self.botao_fechar)

        layout_conteudo.addLayout(layout_botoes)

        layout_principal.addLayout(layout_conteudo, 1)

        # Mensagem inferior
        self.mensagem = QLabel("Nenhum livro cadastrado.")
        self.mensagem.setObjectName("mensagem")

        layout_principal.addWidget(self.mensagem)

        # Conexão dos eventos
        self.botao_cadastrar.clicked.connect(self.cadastrar_livro)
        self.botao_pesquisar.clicked.connect(self.pesquisar_livros)
        self.botao_mostrar_todos.clicked.connect(self.mostrar_todos)
        self.botao_atualizar.clicked.connect(self.atualizar_livro)
        self.botao_excluir.clicked.connect(self.excluir_livro)
        self.botao_limpar.clicked.connect(self.limpar_campos)
        self.botao_fechar.clicked.connect(self.close)

        self.tabela.itemSelectionChanged.connect(
            self.selecionar_livro
        )

        self.campo_pesquisa.returnPressed.connect(
            self.pesquisar_livros
        )

    def cadastrar_livro(self):
        titulo = self.campo_titulo.text().strip()
        autor = self.campo_autor.text().strip()
        ano = self.campo_ano.text().strip()
        isbn = self.campo_isbn.text().strip()

        if not titulo or not autor:
            QMessageBox.warning(
                self,
                "Campos obrigatórios",
                "Preencha o título e o autor.",
            )
            return

        if ano and not ano.isdigit():
            QMessageBox.warning(
                self,
                "Ano inválido",
                "O ano deve conter apenas números.",
            )
            return

        if self.livro_duplicado(
            titulo,
            autor,
            isbn,
        ):
            QMessageBox.warning(
                self,
                "Livro duplicado",
                (
                    "Já existe um livro com o mesmo título "
                    "e autor ou com o mesmo ISBN."
                ),
            )
            return

        livro = {
            "id": self.proximo_id,
            "titulo": titulo,
            "autor": autor,
            "ano": ano,
            "isbn": isbn,
        }

        self.livros.append(livro)
        self.proximo_id += 1

        self.preencher_tabela(self.livros)
        self.limpar_campos()

        self.mensagem.setText(
            f'Livro "{titulo}" cadastrado com sucesso.'
        )

    def preencher_tabela(self, lista_livros):
        self.tabela.setRowCount(0)

        for livro in lista_livros:
            linha = self.tabela.rowCount()
            self.tabela.insertRow(linha)

            item_id = QTableWidgetItem(str(livro["id"]))
            item_titulo = QTableWidgetItem(livro["titulo"])
            item_autor = QTableWidgetItem(livro["autor"])
            item_ano = QTableWidgetItem(livro["ano"])
            item_isbn = QTableWidgetItem(livro["isbn"])

            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_ano.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.tabela.setItem(linha, 0, item_id)
            self.tabela.setItem(linha, 1, item_titulo)
            self.tabela.setItem(linha, 2, item_autor)
            self.tabela.setItem(linha, 3, item_ano)
            self.tabela.setItem(linha, 4, item_isbn)

        quantidade = len(lista_livros)

        self.mensagem.setText(
            f"{quantidade} livro(s) exibido(s)."
        )

    def pesquisar_livros(self):
        termo = self.campo_pesquisa.text().strip().lower()

        if not termo:
            QMessageBox.information(
                self,
                "Pesquisa",
                "Digite um título ou autor para pesquisar.",
            )
            return

        encontrados = []

        for livro in self.livros:
            titulo = livro["titulo"].lower()
            autor = livro["autor"].lower()

            if termo in titulo or termo in autor:
                encontrados.append(livro)

        self.id_selecionado = None
        self.preencher_tabela(encontrados)
        self.atualizar_estado_botoes()

        if not encontrados:
            self.mensagem.setText(
                "Nenhum livro encontrado na pesquisa."
            )

    def mostrar_todos(self):
        self.campo_pesquisa.clear()
        self.id_selecionado = None

        self.preencher_tabela(self.livros)
        self.atualizar_estado_botoes()

    def selecionar_livro(self):
        linha = self.tabela.currentRow()

        if linha < 0:
            self.id_selecionado = None
            self.atualizar_estado_botoes()
            return

        item_id = self.tabela.item(linha, 0)

        if item_id is None:
            return

        self.id_selecionado = int(item_id.text())

        livro_selecionado = None

        for livro in self.livros:
            if livro["id"] == self.id_selecionado:
                livro_selecionado = livro
                break

        if livro_selecionado is None:
            return

        self.campo_titulo.setText(
            livro_selecionado["titulo"]
        )

        self.campo_autor.setText(
            livro_selecionado["autor"]
        )

        self.campo_ano.setText(
            livro_selecionado["ano"]
        )

        self.campo_isbn.setText(
            livro_selecionado["isbn"]
        )

        self.atualizar_estado_botoes()

        self.mensagem.setText(
            f'Livro "{livro_selecionado["titulo"]}" selecionado.'
        )

    def atualizar_livro(self):
        if self.id_selecionado is None:
            QMessageBox.information(
                self,
                "Atualizar",
                "Selecione um livro na tabela.",
            )
            return

        titulo = self.campo_titulo.text().strip()
        autor = self.campo_autor.text().strip()
        ano = self.campo_ano.text().strip()
        isbn = self.campo_isbn.text().strip()

        if not titulo or not autor:
            QMessageBox.warning(
                self,
                "Campos obrigatórios",
                "Preencha o título e o autor.",
            )
            return

        # Verifica ISBN duplicado em outro registro
        if isbn:
            for livro in self.livros:
                if (
                    livro["id"] != self.id_selecionado
                    and livro["isbn"].lower() == isbn.lower()
                ):
                    QMessageBox.warning(
                        self,
                        "ISBN duplicado",
                        "Outro livro já utiliza esse ISBN.",
                    )
                    return

        for livro in self.livros:
            if livro["id"] == self.id_selecionado:
                livro["titulo"] = titulo
                livro["autor"] = autor
                livro["ano"] = ano
                livro["isbn"] = isbn
                break

        self.mostrar_todos()
        self.limpar_campos()

        self.mensagem.setText(
            "Livro atualizado com sucesso."
        )

    def excluir_livro(self):
        if self.id_selecionado is None:
            QMessageBox.information(
                self,
                "Excluir",
                "Selecione um livro na tabela.",
            )
            return

        livro_selecionado = None

        for livro in self.livros:
            if livro["id"] == self.id_selecionado:
                livro_selecionado = livro
                break

        if livro_selecionado is None:
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            (
                f'Deseja realmente excluir o livro '
                f'"{livro_selecionado["titulo"]}"?'
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if resposta == QMessageBox.StandardButton.Yes:
            self.livros.remove(livro_selecionado)

            self.mostrar_todos()
            self.limpar_campos()

            self.mensagem.setText(
                "Livro excluído com sucesso."
            )

    def limpar_campos(self):
        self.campo_titulo.clear()
        self.campo_autor.clear()
        self.campo_ano.clear()
        self.campo_isbn.clear()

        self.tabela.clearSelection()

        self.id_selecionado = None
        self.atualizar_estado_botoes()

        self.campo_titulo.setFocus()

        

    def atualizar_estado_botoes(self):
        registro_selecionado = (
            self.id_selecionado is not None
        )

        self.botao_atualizar.setEnabled(
            registro_selecionado
        )

        self.botao_excluir.setEnabled(
            registro_selecionado
        )

    def aplicar_estilo(self):
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #dcdcdc;
            }

            QWidget {
                font-family: "Segoe UI";
                font-size: 35px;
                color: #000000;
            }

            QLabel#tituloPagina {
                color: #000000;
                font-size: 26px;
                font-weight: bold;
            }

            QLabel#subtitulo {
                color: #000000;
                font-size: 30px;
                margin-bottom: 30px;
            }

            QLabel#mensagem {
                color: #475569;
                background-color: #e2e8f0;
                border: 1px solid #94a3b8;
                border-radius: 6px;
                padding: 8px;
            }

            QLineEdit {
                background-color: white;
                color: #000000;
                border: 2px solid #b8c4d2;
                border-radius: 6px;
                padding: 8px;
            }

            QLineEdit:hover {
                border: 2px solid #60a5fa;
                background-color: #f8fafc;

            }

            QLineEdit:focus {
                border: 3px solid #2563eb;
                background-color: #ffffff;

            }

            QPushButton {
                min-width: 140px;
                background-color: #e2e8f0;
                color: #000000;
                border: 2px solid #94a3b8;
                border-radius: 8px;
                padding: 9px 12px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #cbd5e1;
            }

            QPushButton#botaoCadastrar,
            QPushButton#botaoAtualizar {
            QPushButton#botaoExcluir,
            QPushButton#botaoLimpar,
            QPushButton#botaoFechar {
                background-color: #000000;
                color: #ffffff;
                border: 3px solid #ffd700;
                border-radius: 8px;
                padding: 9px 12px;
                font-weight: bold;

            QPushButton#botaoCadastrar:hover,
            QPushButton#botaoAtualizar:hover,
            QPushButton#botaoExcluir:hover,
            QPushButton#botaoLimpar:hover,
            QPushButton#botaoFechar:hover {
                background-color: #00008b;
                color: #ffffff;
                border: 3px solid #00ffff;    
                
            QPushButton:disabled {
                background-color: #e5e7eb;
                color: #9ca3af;
            }

            QPushButton#botaoCadastrar {
                background-color: #000000;
                color: white;
                border: 10px solid #ffd700;
            }

            QPushButton#botaoCadastrar:hover {
                background-color: #00008b;
            }

            QPushButton#botaoAtualizar {
                background-color: #000000;
                color: white;
                
            }

            QPushButton#botaoExcluir {
                background-color: #000000;
                color: white;
                
            }

            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f8fafc;
                color: #000000;
                border: 2px solid #cbd5e1;
                border-radius: 8px;
                gridline-color: #e2e8f0;
                selection-background-color: #bfdbfe;
                selection-color: #1e3a8a;
            }

            QTableWidget::viewport {
                background-color: #ffffff;
            }

            QHeaderView::section {
                background-color: #173b6c;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }

            QPushButton#botaoLimpar {
                border: 2px solid #000000;
                background-color: #000000;
                color: #ffffff;
            }

            QPushButton#botaoLimpar:hover {
                border: 2px solid #60a5fa;
                background-color: #00008b;
            }

            QPushButton#botaoLimpar:pressed {
                border: 3px solid #93c5fd;
                background-color: #000066;
            }

            QPushButton#botaoFechar {
                background-color: #000000;
                color: #ffffff;
            }

            QPushButton#botaoFechar:hover {
                background-color: #b91c1c;
            }

            QPushButton#botaoFechar:pressed {
                background-color: #7f1d1d;
            }
            """
        )


if __name__ == "__main__":
    aplicativo = QApplication(sys.argv)

    janela = GerenciadorLivros()
    janela.showMaximized()

    sys.exit(aplicativo.exec())