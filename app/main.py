import json
import xml.etree.ElementTree as ET
import ssl
import websockets
from enums import Type

from utils import *
from youtube_music import (
    YoutubeMusic,
)
from tts import TTS

HOST = "127.0.0.1"
not_quit = True
intent_not_undestand_well = None
list_intent = [
    "search_music",
    "play_playlist",
    "add_music_to_playlist",
    "add_music_to_queue",
    "wich_music_is_playing",
    "control_music",
    "change_track",
    "adjust_volume",
    "set_mode",
    "add_to_favorites",
    "confirm_action",
    "goodbye",
    "help",
]


async def message_handler(youtube_music: YoutubeMusic, message: str):
    message, typ = process_message(message)

    if typ == Type.SPEECH:
        speech_control(youtube_music, message)
    elif typ == Type.GESTURE:
        gesture_control(youtube_music, message)
    elif typ == Type.OK:
        return


def gesture_control(youtube_music, message):
    return


def speech_control(youtube_music, message):
    global intent_not_undestand_well
    message = process_message(message)
    print(f"Message received: {message}")

    if message == "OK":
        return "OK"

    intent = message["intent"]["name"]
    confidence = message["intent"]["confidence"]
    entities = message.get("entities", [])

    if intent not in list_intent:
        youtube_music.tts(random_not_understand())
        return
    elif intent == "confirm_action":
        if intent_not_undestand_well:
            if message["intent"]["name"] == "confirm_action":
                if (
                    message["intent"]["confidence"] > 0.7
                    and message["entities"][0]["value"] == "confirm"
                ):
                    intent = intent_not_undestand_well.intent
                    entities = intent_not_undestand_well.entities
                    youtube_music.tts("Ok, vou fazer o que pediste.")
                else:
                    youtube_music.tts("Não entendi o que disseste.")
            else:
                youtube_music.tts("Ok, não vou fazer nada.")

            intent_not_undestand_well = None
        else:
            youtube_music.tts(random_not_understand())

    elif confidence <= 0.45:
        youtube_music.tts(random_not_understand())
        return
    elif confidence > 0.45 and confidence < 0.8:
        intent_not_undestand_well = IntentNotUnderstoodWell(intent, entities)
        youtube_music.tts(intent_not_sure(intent, entities))
        return

    if intent == "control_music":  # DONE
        # Pausar ou continuar
        action = next((e["value"] for e in entities if e["entity"] == "action"), None)
        if action == "pause":
            youtube_music.pause()
        elif action == "resume":
            youtube_music.resume()
        else:
            youtube_music.tts("Não percebi se queres pausar ou continuar a música.")

    elif intent == "change_track":  # DONE
        # Mudar para próxima ou anterior
        direction = next(
            (e["value"] for e in entities if e["entity"] == "direction"), None
        )
        if direction == "next":
            youtube_music.next_song()
        elif direction == "previous":
            youtube_music.previous_song()
        elif direction == "same":
            youtube_music.repeat_song()
        else:
            youtube_music.tts(
                "Não percebi se queres passar para a póxima música, ir para a anterior ou repetir esta música."
            )

    elif intent == "adjust_volume":  # DONE
        action = next((e["value"] for e in entities if e["entity"] == "action"), None)
        if action == "increase":
            youtube_music.increase_volume()
        elif action == "decrease":
            youtube_music.decrease_volume()
        elif action == "mute":
            youtube_music.mute()
        elif action == "unmute":
            youtube_music.unmute()
        else:
            youtube_music.tts(
                "Não percebi de queres aumentar, diminuir, desloigar ou ligar o som."
            )

    elif intent == "set_mode":  # DONE
        mode = next((e["value"] for e in entities if e["entity"] == "mode"), None)
        if mode == "shuffle_on":
            youtube_music.shuffle_on()
        elif mode == "shuffle_off":
            youtube_music.shuffle_off()
        elif mode == "repeat_one":
            youtube_music.repeat_one()
        elif mode == "repeat_all":
            youtube_music.repeat_all()
        elif mode == "repeat_off":
            youtube_music.repeat_off()
        else:
            youtube_music.tts("Não percebi qual o modo queres colocar.")

    elif intent == "add_to_favorites":  # DONE
        youtube_music.like_music()

    elif intent == "search_music":  # DONE
        song = next((e["value"] for e in entities if e["entity"] == "song"), None)
        artist = next((e["value"] for e in entities if e["entity"] == "artist"), None)

        if song and artist:
            youtube_music.search_music(song, artist)
            youtube_music.play_music_searched()
        else:
            if not song and not artist:
                youtube_music.tts("Não percebi o nome nem o artista.")
            elif not song:
                youtube_music.tts("Não percebi o nome da música.")
            elif not artist:
                youtube_music.tts("Não percebi o nome do artista.")

    elif intent == "add_music_to_queue":  # DONE
        song = next((e["value"] for e in entities if e["entity"] == "song"), None)
        artist = next((e["value"] for e in entities if e["entity"] == "artist"), None)

        if song and artist:
            youtube_music.search_music(song, artist)
            youtube_music.add_to_queue()
        else:
            if not song and not artist:
                youtube_music.tts("Não percebi o nome nem o artista.")
            elif not song:
                youtube_music.tts("Não percebi o nome da música.")
            elif not artist:
                youtube_music.tts("Não percebi o nome do artista.")

    elif intent == "wich_music_is_playing":  # DONE
        youtube_music.get_current_music()

    elif intent == "play_playlist":  # DONE
        playlist = next(
            (e["value"] for e in entities if e["entity"] == "playlist"), None
        )

        if playlist:
            youtube_music.play_playlist(playlist)
        else:
            youtube_music.tts("Não percebi o nome da playlist.")

    elif intent == "add_music_to_playlist":  # DONE
        song = next((e["value"] for e in entities if e["entity"] == "song"), None)
        artist = next((e["value"] for e in entities if e["entity"] == "artist"), None)
        playlist = next(
            (e["value"] for e in entities if e["entity"] == "playlist"), None
        )

        if song and artist and playlist:
            youtube_music.search_music(song, artist)
            youtube_music.add_music_to_playlist(playlist)
        else:
            if not song and not artist and not playlist:
                youtube_music.tts(
                    "Não percebi o nome da música, do artista e da playlist."
                )
            elif not song and not artist:
                youtube_music.tts("Não percebi o nome da música e do artista.")
            elif not song and not playlist:
                youtube_music.tts("Não percebi o nome da música e da playlist.")
            elif not artist and not playlist:
                youtube_music.tts("Não percebi o nome do artista e da playlist.")
            elif not song:
                youtube_music.tts("Não percebi o nome da música.")
            elif not artist:
                youtube_music.tts("Não percebi o nome do artista.")
            elif not playlist:
                youtube_music.tts("Não percebi o nome da playlist.")

    elif intent == "help":  # DONE
        option = next(
            (e["value"] for e in entities if e["entity"] == "help_option"), None
        )

        if option:
            youtube_music.help(option)
        else:
            youtube_music.help()

    elif intent == "goodbye":  # DONE
        youtube_music.tts(random_goodbye())
        youtube_music.close()
        global not_quit
        not_quit = False

    else:
        youtube_music.tts(random_not_understand())


def intent_not_sure(intent, entities):
    if intent == "control_music":
        action = next((e["value"] for e in entities if e["entity"] == "action"), None)

        if action == "pause":
            return "Penso que disseste que querias pausar a música, está certo?"
        elif action == "resume":
            return "Penso que disseste que querias continuar a música, está certo?"

    elif intent == "change_track":
        direction = next(
            (e["value"] for e in entities if e["entity"] == "direction"), None
        )

        if direction == "next":
            return "Penso que disseste que querias mudar para a próxima música, está certo?"
        elif direction == "previous":
            return "Penso que disseste que querias mudar para a música anterior, está certo?"
        elif direction == "same":
            return "Penso que disseste que querias repetir a música atual, está certo?"

    elif intent == "adjust_volume":
        action = next((e["value"] for e in entities if e["entity"] == "action"), None)

        if action == "increase":
            return "Penso que disseste que querias aumentar o volume, está certo?"
        elif action == "decrease":
            return "Penso que disseste que querias diminuir o volume, está certo?"
        elif action == "mute":
            return "Penso que disseste que querias silenciar a música, está certo?"
        elif action == "unmute":
            return "Penso que disseste que querias ativar o som, está certo?"

    elif intent == "set_mode":
        mode = next((e["value"] for e in entities if e["entity"] == "mode"), None)

        if mode == "shuffle_on":
            return "Penso que disseste que querias ativar o modo aleatório, está certo?"
        elif mode == "shuffle_off":
            return (
                "Penso que disseste que querias desativar o modo aleatório, está certo?"
            )
        elif mode == "repeat_one":
            return "Penso que disseste que querias repetir a música atual, está certo?"
        elif mode == "repeat_all":
            return "Penso que disseste que querias repetir a lista de reprodução, está certo?"
        elif mode == "repeat_off":
            return "Penso que disseste que querias desativar a repetição, está certo?"

    elif intent == "add_to_favorites":
        return "Penso que disseste que querias adicionar a música aos favoritos, está certo?"

    elif intent == "search_music":
        song = next((e["value"] for e in entities if e["entity"] == "song"), None)
        artist = next((e["value"] for e in entities if e["entity"] == "artist"), None)

        return f"Penso que disseste que querias pesquisar a música '{song}' de {artist}, está certo?"

    elif intent == "add_music_to_queue":
        song = next((e["value"] for e in entities if e["entity"] == "song"), None)
        artist = next((e["value"] for e in entities if e["entity"] == "artist"), None)

        return f"Penso que disseste que querias adicionar a música '{song}' de {artist} à fila de reprodução, está certo?"

    elif intent == "wich_music_is_playing":
        return "Penso que disseste que querias saber qual a música que está a tocar, está certo?"

    elif intent == "play_playlist":
        playlist = next((e["value"] for e in entities if e["entity"] == "playlist"), "")

        return (
            f"Penso que disseste que querias tocar a playlist '{playlist}', está certo?"
        )

    elif intent == "add_music_to_playlist":
        song = next((e["value"] for e in entities if e["entity"] == "song"), None)
        artist = next((e["value"] for e in entities if e["entity"] == "artist"), None)
        playlist = next(
            (e["value"] for e in entities if e["entity"] == "playlist"), None
        )

        return f"Penso que disseste que querias adicionar a música '{song}' de {artist} à playlist '{playlist}', está certo?"

    elif intent == "help":
        option = next(
            (e["value"] for e in entities if e["entity"] == "help_option"), None
        )

        if option:
            return f"Penso que disseste que querias ajuda sobre '{option}', está certo?"
        else:
            return "Penso que disseste que querias ajuda, está certo?"

    elif intent == "goodbye":
        return "Penso que disseste que querias fechar o aplicativo, está certo?"


def process_message(message):
    """Processa a mensagem recebida e extrai NLU."""
    if message == "OK":
        return "OK"

    commands = ET.fromstring(message).findall(".//command")
    json_command = commands.pop(0).text
    command = json.loads(json_command)
    modality = command["recognized"][0]

    if modality == "SPEECH":
        return json.loads(command["nlu"]), Type.SPEECH
    elif modality == "GESTURES":
        return command["recognized"][1], Type.GESTURE
    elif modality == "FUSION":
        return (command["recognized"][1:], commands), Type.FUSION


async def main():
    tts = TTS(FusionAdd=f"https://{HOST}:8000/IM/USER1/APPSPEECH").sendToVoice
    youtube_music = YoutubeMusic(
        TTS=tts
    )  # Crie uma classe MusicPlayer para controlar a reprodução de músicas
    mmi_cli_out_add = f"wss://{HOST}:8005/IM/USER1/APP"

    # SSL config
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Connect to websocket
    async with websockets.connect(mmi_cli_out_add, ssl=ssl_context) as websocket:
        print("Connected to MMI CLI OUT")

        while not_quit:
            try:
                msg = await websocket.recv()
                await message_handler(youtube_music=youtube_music, message=msg)
            except Exception as e:
                tts("Ocorreu um erro, a fechar o aplicativo")
                print(f"Error: {e}")

        print("Closing connection")
        await websocket.close()
        print("Connection closed")
        exit(0)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
