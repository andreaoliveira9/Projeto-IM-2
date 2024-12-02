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


class IntentNotUnderstoodWell:
    def __init__(self, intent, entities):
        self.intent = intent
        self.entities = entities

    def __str__(self):
        return f"Intent: {self.intent}, Entities: {self.entities}"
