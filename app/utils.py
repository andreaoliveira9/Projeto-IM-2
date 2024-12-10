import random


# Decorator para randomizar as respostas TTS para cada intenção
def randomize(func):
    def wrapper(*args, **kwargs):
        return random.choice(func(*args, **kwargs))

    return wrapper


@randomize
def random_goodbye():
    return [
        "Até logo! Espero que tenha gostado da música!",
        "Tchau! Volte sempre para ouvir mais!",
        "Adeus! Até a próxima!",
        "Tchau! Espero que você tenha uma boa música!",
        "Até mais! Estou aqui quando você precisar!",
    ]


@randomize
def random_not_understand():
    return [
        "Desculpe, não entendi o que pediu.",
        "Não compreendi o comando, pode repetir?",
        "Pode dizer novamente? Não entendi.",
        "Desculpe, não reconheci o pedido.",
        "Comando não entendido, pode tentar de novo?",
    ]


class IntentNotUnderstoodWellVoice:
    def __init__(self, intent, entities):
        self.intent = intent
        self.entities = entities

    def confirmation(self):
        if self.intent == "control_music":
            action = next(
                (e["value"] for e in self.entities if e["entity"] == "action"), None
            )

            if action == "pause":
                return "Penso que disseste que querias pausar a música, está certo?"
            elif action == "resume":
                return "Penso que disseste que querias continuar a música, está certo?"

        elif self.intent == "change_track":
            direction = next(
                (e["value"] for e in self.entities if e["entity"] == "direction"), None
            )

            if direction == "next":
                return "Penso que disseste que querias mudar para a próxima música, está certo?"
            elif direction == "previous":
                return "Penso que disseste que querias mudar para a música anterior, está certo?"
            elif direction == "same":
                return (
                    "Penso que disseste que querias repetir a música atual, está certo?"
                )

        elif self.intent == "adjust_volume":
            action = next(
                (e["value"] for e in self.entities if e["entity"] == "action"), None
            )

            if action == "increase":
                return "Penso que disseste que querias aumentar o volume, está certo?"
            elif action == "decrease":
                return "Penso que disseste que querias diminuir o volume, está certo?"
            elif action == "mute":
                return "Penso que disseste que querias silenciar a música, está certo?"
            elif action == "unmute":
                return "Penso que disseste que querias ativar o som, está certo?"

        elif self.intent == "set_mode":
            mode = next(
                (e["value"] for e in self.entities if e["entity"] == "mode"), None
            )

            if mode == "shuffle_on":
                return "Penso que disseste que querias ativar o modo aleatório, está certo?"
            elif mode == "shuffle_off":
                return "Penso que disseste que querias desativar o modo aleatório, está certo?"
            elif mode == "repeat_one":
                return (
                    "Penso que disseste que querias repetir a música atual, está certo?"
                )
            elif mode == "repeat_all":
                return "Penso que disseste que querias repetir a lista de reprodução, está certo?"
            elif mode == "repeat_off":
                return (
                    "Penso que disseste que querias desativar a repetição, está certo?"
                )

        elif self.intent == "add_to_favorites":
            return "Penso que disseste que querias adicionar a música aos favoritos, está certo?"

        elif self.intent == "search_music":
            song = next(
                (e["value"] for e in self.entities if e["entity"] == "song"), None
            )
            artist = next(
                (e["value"] for e in self.entities if e["entity"] == "artist"), None
            )

            return f"Penso que disseste que querias pesquisar a música '{song}' de {artist}, está certo?"

        elif self.intent == "add_music_to_queue":
            song = next(
                (e["value"] for e in self.entities if e["entity"] == "song"), None
            )
            artist = next(
                (e["value"] for e in self.entities if e["entity"] == "artist"), None
            )

            return f"Penso que disseste que querias adicionar a música '{song}' de {artist} à fila de reprodução, está certo?"

        elif self.intent == "wich_music_is_playing":
            return "Penso que disseste que querias saber qual a música que está a tocar, está certo?"

        elif self.intent == "play_playlist":
            playlist = next(
                (e["value"] for e in self.entities if e["entity"] == "playlist"), ""
            )

            return f"Penso que disseste que querias tocar a playlist '{playlist}', está certo?"

        elif self.intent == "add_music_to_playlist":
            song = next(
                (e["value"] for e in self.entities if e["entity"] == "song"), None
            )
            artist = next(
                (e["value"] for e in self.entities if e["entity"] == "artist"), None
            )
            playlist = next(
                (e["value"] for e in self.entities if e["entity"] == "playlist"), None
            )

            return f"Penso que disseste que querias adicionar a música '{song}' de {artist} à playlist '{playlist}', está certo?"

        elif self.intent == "help":
            option = next(
                (e["value"] for e in self.entities if e["entity"] == "help_option"),
                None,
            )

            if option:
                return f"Penso que disseste que querias ajuda sobre '{option}', está certo?"
            else:
                return "Penso que disseste que querias ajuda, está certo?"

        elif self.intent == "goodbye":
            return "Penso que disseste que querias fechar o aplicativo, está certo?"

    def __str__(self):
        return f"Intent: {self.intent}, Entities: {self.entities}"
