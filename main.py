import threading
import queue
from tkinter import *
import tkinter.messagebox

from tic_tac_toe_api import get_list_of_games, create_game, connected_second_player, make_move, waiting_move, \
    connect_second_player
from utils import all_children


class MainWindow:
    def __init__(self):
        self.main_window = Tk()
        self.main_window.title('tic-tac-toe')

        self.queue = queue.Queue()

        self.games_listbox = None
        self.label_n = None
        self.label_d = None
        self.n = None
        self.d = None
        self.n_entry = None
        self.d_entry = None
        self.btn_create_game = None
        self.btn_connect_to_game = None
        self.buttons = []
        self.board = None
        self.size_of_board = 3
        self.length_of_win_comb = 3
        self.move = 'X'
        self.can_i_move = True
        self.list_of_games = None

    def start_app(self):
        self.main_window.mainloop()

    def draw_menu(self):
        self.main_window.geometry('750x400+400+100')

        self.render_list_of_games()

        self.label_n = Label(text='Размерность')
        self.label_d = Label(text='Длина комбинации')

        self.label_n.place(x=30, y=30)
        self.label_d.place(x=30, y=50)

        self.n = StringVar()
        self.d = StringVar()

        self.n_entry = Entry(textvariable=self.n)
        self.d_entry = Entry(textvariable=self.d)
        self.n_entry.insert(END, '3')
        self.d_entry.insert(END, '3')

        self.n_entry.place(x=200, y=30, width=50)
        self.d_entry.place(x=200, y=50, width=50)

        self.btn_create_game = Button(text='Создать игру', command=self.start_game)
        self.btn_create_game.place(x=30, y=75, width=220)

        self.btn_connect_to_game = Button(text='Присоединиться к игре', command=self.connect_to_game)
        self.btn_connect_to_game.place(x=30, y=110, width=220)

        self.btn_connect_to_game = Button(text='Обновить список', command=self.render_list_of_games)
        self.btn_connect_to_game.place(x=30, y=145, width=220)

        self.queue.put('menu')

    def render_list_of_games(self):
        self.games_listbox = Listbox()
        self.list_of_games = get_list_of_games()
        for game in self.list_of_games:
            self.games_listbox.insert(END, f'{game["game_id"]} {game["size_of_board"]} {game["length_of_win_comb"]}')
        self.games_listbox.place(x=300, y=30, width=400, height=300)

    def connect_to_game(self):
        self.queue.put('connect')

    def start_game(self):
        n, d = self.n.get(), self.d.get()

        if not n.isdigit() or not d.isdigit():
            return

        self.size_of_board, self.length_of_win_comb = int(n), int(d)

        self.queue.put('create_game')

    def start_waiting(self):
        self.label_wait = Label(text='Ожидание второго игрока')
        self.label_wait.pack()

    def draw_fields(self):
        self.main_window.geometry('600x700+400+100')

        for i in range(self.size_of_board):
            row_buttons = []
            for j in range(self.size_of_board):
                btn = Button(command=lambda x=i, y=j: self.btn_click(x, y), text='', width=4, height=2)
                btn.grid(row=i, column=j)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

        self.label_player = Label(text=f'You: {self.move}')
        self.label_player.grid(row=i+1)

        self.board = '-' * self.size_of_board ** 2

    def render_fields(self):
        i = 0
        for row in self.buttons:
            for btn in row:
                if self.board[i] != '-':
                    btn['text'] = self.board[i]
                else:
                    btn['text'] = ''
                i += 1

    def clear_all(self):
        children = all_children(self.main_window)
        for child in children:
            child.destroy()

    def btn_click(self, x, y):
        if main_window.buttons[x][y]['text'] or not self.can_i_move:
            return
        main_window.buttons[x][y]['text'] = self.move
        board = ''
        for row in main_window.buttons:
            for btn in row:
                if btn['text']:
                    board += btn['text']
                else:
                    board += '-'
        self.board = board
        self.queue.put('move')

    def alert(self, phrase):
        for row in self.buttons:
            for btn in row:
                btn.configure(state=DISABLED)
        tkinter.messagebox.showinfo('tic-tac-toe', phrase)



def game():
    global main_window
    game_id = None
    player_key = None
    while True:
        command = main_window.queue.get()

        if command == 'create_game':
            game_id, player_key = create_game(main_window.size_of_board, main_window.length_of_win_comb)

            main_window.clear_all()
            main_window.start_waiting()
            if connected_second_player(game_id, player_key):
                main_window.clear_all()
                main_window.draw_fields()
            else:
                pass  # Второй игрок не подключился
        elif command == 'move':
            winner = make_move(game_id, player_key, main_window.board)
            main_window.can_i_move = False
            if winner == '-':
                board, winner = waiting_move(game_id, player_key)
                main_window.board = board
                main_window.render_fields()
                main_window.can_i_move = True
            if winner == 'O' or winner == 'X':
                main_window.alert(f'win {winner}')
            if winner == 'draw':
                main_window.alert('Ничья!')

        elif command == 'connect':
            i = main_window.games_listbox.curselection()

            if not i:
                return

            selection = main_window.list_of_games[i[0]]
            main_window.can_i_move = False
            main_window.move = 'O'

            game_id = selection['game_id']

            player_key = connect_second_player(game_id)

            main_window.size_of_board = int(selection['size_of_board'])
            main_window.length_of_win_comb = int(selection['length_of_win_comb'])

            main_window.clear_all()
            main_window.draw_fields()

            board, winner = waiting_move(game_id, player_key)

            if winner != '-':
                main_window.alert_winner(winner)

            main_window.board = board
            main_window.render_fields()
            main_window.can_i_move = True



main_window = MainWindow()
main_window.draw_menu()

my_thread = threading.Thread(target=game)
my_thread.daemon = True
my_thread.start()

main_window.start_app()



