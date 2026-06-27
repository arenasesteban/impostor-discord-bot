from src.game.session import Session


game = Session(host_id=1)

game.add_player(2)
game.add_player(3)

roles = game.start_game(secret_word="pizza")

print("Jugadores:", game.players)
print("Impostor:", game.impostor_id)
print("Roles:", roles)