from peewee import *
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import filedialog

db = SqliteDatabase("Manager.db")


class BaseModel(Model):
    class Meta:
        database = db

class Product(BaseModel):
    nome = CharField()
    preco = DecimalField(max_digits=10, decimal_places=2)

class Sell(BaseModel):
    produto = ForeignKeyField(Product, backref="vendas")
    quantidade = IntegerField()
    total = DecimalField(max_digits=17, decimal_places=2)

db.connect()
db.create_tables([Product, Sell])




#SALES=====================================================

def sales_window():
    sales_win = tk.Toplevel()
    sales_win.title("Cadastrar Venda")
    sales_win.geometry("500x400")

    
    style = Style()
    style.configure("TButton", font=("Arial", 12), padding=5)

    
    vendas = []

    
    Label(sales_win, text="Selecione o Produto", font=("Arial", 12)).pack(padx=15, pady=5)
    produto_cb = Combobox(sales_win, font=("Arial", 12))

    
    produtos = [product.nome for product in Product.select()]
    produto_cb["values"] = produtos
    produto_cb.pack(padx=15, pady=5)

    
    Label(sales_win, text="Quantidade", font=("Arial", 12)).pack(padx=15, pady=5)
    quantidade_entry = Entry(sales_win, font=("Arial", 12))
    quantidade_entry.pack(padx=15, pady=5)

    
    tree = Treeview(sales_win, columns=("Produto", "Quantidade", "Preço Unitário", "Subtotal"), show="headings")
    tree.heading("Produto", text="Produto")
    tree.heading("Quantidade", text="Quantidade")
    tree.heading("Preço Unitário", text="Preço Unitário")
    tree.heading("Subtotal", text="Subtotal")
    tree.pack(fill=BOTH, expand=True, padx=15, pady=10)

    
    def adicionar_produto():
        produto_nome = produto_cb.get().strip()
        quantidade_str = quantidade_entry.get().strip()

        if not produto_nome or not quantidade_str:
            messagebox.showerror("Erro", "Preencha todos os campos")
            return

        
        try:
            quantidade = int(quantidade_str)
        except ValueError:
            messagebox.showerror("Erro", "Digite uma quantidade válida")
            return

        
        try:
            produto = Product.get(Product.nome == produto_nome)
        except Product.DoesNotExist:
            messagebox.showerror("Erro", "Produto não encontrado")
            return

        
        subtotal = produto.preco * quantidade
        
        
        vendas.append((produto, quantidade))

        
        tree.insert("", "end", values=(produto.nome, quantidade, f"R$ {produto.preco:.2f}", f"R$ {subtotal:.2f}"))

        

        
        produto_cb.set("")
        quantidade_entry.delete(0, END)

    
    def registrar_venda():
        if not vendas:
            messagebox.showerror("Erro", "Adicione pelo menos um produto para realizar a venda")
            return

        
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                   filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                                                   title="Salvar Venda como")

        if not file_path:  
            return

        
        with open(file_path, "a") as file:
            file.write("Nota de Venda\n")
            file.write("-" * 30 + "\n")

            total_venda = 0

            for produto, quantidade in vendas:
                subtotal = produto.preco * quantidade
                total_venda += subtotal

                
                file.write(f"Produto: {produto.nome}\n")
                file.write(f"Quantidade: {quantidade}\n")
                file.write(f"Preço Unitário: R$ {produto.preco:.2f}\n")
                file.write(f"Subtotal: R$ {subtotal:.2f}\n")
                file.write("-" * 30 + "\n")

            file.write(f"Total Geral: R$ {total_venda:.2f}\n")
            file.write("=" * 30 + "\n\n")

        messagebox.showinfo("Sucesso", f"Venda registrada com sucesso!\nTotal: R$ {total_venda:.2f}")

        
        vendas.clear()
        for row in tree.get_children():
            tree.delete(row)

    
    Button(sales_win, text="Adicionar Produto", command=adicionar_produto, style="TButton").pack(pady=10)

    
    Button(sales_win, text="Confirmar Venda", command=registrar_venda, style="TButton").pack(pady=10)
#=========================================================
#===========MANAGE WINDOW=================================
def manage_window():
    manage = tk.Toplevel()
    manage.title("Gerenciar Produtos")
    manage.geometry("500x500")

    
    style = Style()
    style.configure("TButton", font=("Arial", 12), padding=5)

    
    title_label = tk.Label(manage, text="Gerenciar Produtos", font=("Arial", 16, "bold"))
    title_label.pack(pady=10)

    
    tree = Treeview(manage, columns=("nome", "preco"), show="headings", height=10)
    tree.heading("nome", text="Nome do Produto")
    tree.heading("preco", text="Preço")

    
    tree.column("nome", anchor="center", width=200)
    tree.column("preco", anchor="center", width=100)

    tree.pack(fill=BOTH, expand=True, padx=15, pady=10)

    def load_products():
        for row in tree.get_children():
            tree.delete(row)

        for product in Product.select():
            tree.insert("", END, values=(product.nome, f"R$: {product.preco :.2f}"))

    load_products()

    
    def edit_window():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Selecione um produto para editar")
            return

        item = tree.item(selected_item)
        product_values = item["values"]

        old_name = product_values[0]
        old_preco = product_values[1].replace("R$: ", "")

        edit_win = tk.Toplevel(manage)
        edit_win.title("Editar Produto")
        edit_win.geometry("300x200")

        tk.Label(edit_win, text="Nome do Produto", font=("Arial", 12)).pack(padx=15, pady=5)
        nome_entry = Entry(edit_win, font=("Arial", 12))
        nome_entry.pack(padx=15, pady=5)
        nome_entry.insert(0, old_name)

        tk.Label(edit_win, text="Preço do Produto", font=("Arial", 12)).pack(padx=15, pady=5)
        preco_entry = Entry(edit_win, font=("Arial", 12))
        preco_entry.pack(padx=15, pady=5)
        preco_entry.insert(0, old_preco)

        def save_edit():
            new_name = nome_entry.get().strip()
            new_price = preco_entry.get().strip()

            if not new_name or not new_price:
                messagebox.showerror("Erro", "Todos os campos devem ser preenchidos")
                return

            try:
                new_price = float(new_price)
            except ValueError:
                messagebox.showerror("Erro", "Coloque um preço válido")
                return

            product = Product.get(Product.nome == old_name)
            product.nome = new_name
            product.preco = new_price
            product.save()

            messagebox.showinfo("Sucesso", "Produto Atualizado")
            load_products()
            edit_win.destroy()

        Button(edit_win, text="Salvar", command=save_edit, style="TButton").pack(pady=10)

    
    def delete_product():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Selecione um produto para deletar")
            return

        item = tree.item(selected_item)
        product_values = item["values"]
        product_name = product_values[0]

        confirm = messagebox.askyesno("Confirmação", f"Tem certeza que deseja deletar o produto: {product_name}?")
        if confirm:
            product = Product.get(Product.nome == product_name)
            product.delete_instance()
            messagebox.showinfo("Sucesso", "Produto deletado com sucesso")
            load_products()

    
    button_frame = tk.Frame(manage)
    button_frame.pack(pady=10)

    edit_button = Button(button_frame, text="Editar Produto", command=edit_window, style="TButton")
    edit_button.grid(row=0, column=0, padx=10)

    delete_button = Button(button_frame, text="Deletar Produto", command=delete_product, style="TButton")
    delete_button.grid(row=0, column=1, padx=10)

#======================================================================================
#====================INSERT=========================================
def insert_window():
    def insert():
        nome = produto_entry.get().strip()
        preco = preco_entry.get().strip()

        if not nome or not preco:
            messagebox.showerror("Erro", "Preencha todos os campos")
            return
        
        try:
            preco = float(preco)
        except ValueError:
            messagebox.showerror("Erro", "Entre com um preço válido")
            return

        produto = Product.create(nome=nome, preco=preco)
        messagebox.showinfo("Cadastrado", "O produto: " + produto.nome + " foi cadastrado")

        produto_entry.delete(0, END)
        preco_entry.delete(0, END)

    root.withdraw()
    insertwin = tk.Toplevel()
    insertwin.title("Inserir Produto")
    insertwin.geometry("400x300")

    
    insertStyle = Style()
    insertStyle.configure('W.TButton', font=("Arial", 12), padding=5)

    
    Label(insertwin, text="Nome do Produto", font=("Arial", 12)).pack(padx=15, pady=15)
    produto_entry = Entry(insertwin, font=("Arial", 12))
    produto_entry.pack(padx=15, pady=15)

    Label(insertwin, text="Preço do Produto", font=("Arial", 12)).pack(padx=15, pady=15)
    preco_entry = Entry(insertwin, font=("Arial", 12))
    preco_entry.pack(padx=15, pady=15)

    
    insert_button = Button(insertwin, text="Cadastrar", command=insert, style='W.TButton')
    insert_button.pack(pady=15)

    insertwin.protocol("WM_DELETE_WINDOW", lambda: (root.deiconify(), insertwin.destroy()))

#======================================================================
def load_products():
    for row in tree.get_children():
        tree.delete(row)

    for product in Product.select():
        tree.insert("", END, values=(product.nome, f"R$: {product.preco :.2f}"))
    
def search_item(search_term):
    search_term = search_term.strip().lower()
    if not search_term:
        messagebox.showerror("Erro", "Digite um produto válido")
    for row in tree.get_children():
        tree.delete(row)

    query = Product.select().where(Product.nome.contains(search_term))
    for product in query:
        tree.insert("", END, values=(product.nome, f"R$: {product.preco :.2f}"))


root = tk.Tk()
root.geometry("500x500")
root.title("PDV mais Basico do mundo")


menubar = Menu(root)


crudmenu = Menu(menubar, tearoff=0)
crudmenu.add_command(label="Novo produto", command=insert_window)
crudmenu.add_command(label="Gerenciar Produtos", command=manage_window)

sales_menu = Menu(menubar, tearoff=0)
sales_menu.add_command(label="Realizar Venda", command=sales_window)


menubar.add_cascade(label="Produtos", menu=crudmenu)
menubar.add_cascade(label="Vendas", menu=sales_menu)


search = Entry(root, font=("Arial", 12))
search.pack(padx=5, pady=5)

Button(root, text="Pesquisar", command=lambda: search_item(search.get()), style='TButton').pack(padx=10, pady=5)


tree = Treeview(root, columns=("nome", "preco"), show="headings")
tree.heading("nome", text="Nome do Produto")
tree.heading("preco", text="Preço")
tree.pack(fill=BOTH, expand=True)

load_products()


root.config(menu=menubar)
root.mainloop()
