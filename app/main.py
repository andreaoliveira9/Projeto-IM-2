import json
import xml.etree.ElementTree as ET
import ssl
import websockets
from enums import Type
import time

from utils import *
from youtube_music import YoutubeMusic
from tts import TTS

HOST = "127.0.0.1"
not_quit = True
intent_not_undestand_well_voice = None
gesture_confirmation = None


def process_message(message):
    if message == "OK":
        return message, Type.OK

    json_command = ET.fromstring(message).find(".//command").text
    command = json.loads(json_command)

    if "nlu" in command:
        return json.loads(command["nlu"]), Type.SPEECH
    elif "recognized" in command:
        return command["recognized"][1], Type.GESTURE


async def message_handler(youtube_music: YoutubeMusic, message: str):
    message, typ = process_message(message)

    """ typ = Type.GESTURE
    message = "OPENEXPLORE" """
    if typ == Type.SPEECH:
        speech_control(youtube_music, message)
    elif typ == Type.GESTURE:
        gesture_control(youtube_music, message)
    elif typ == Type.OK:
        return

    """ time.sleep(1)

    for i in range(1):
        typ = Type.GESTURE
        message = "SCROLLDOWNCATEGORY"
        if typ == Type.SPEECH:
            speech_control(youtube_music, message)
        elif typ == Type.GESTURE:
            gesture_control(youtube_music, message)
        elif typ == Type.OK:
            return

        time.sleep(1)

    for i in range(1):
        typ = Type.GESTURE
        message = "MOVERIGHTCATEGORY"
        if typ == Type.SPEECH:
            speech_control(youtube_music, message)
        elif typ == Type.GESTURE:
            gesture_control(youtube_music, message)
        elif typ == Type.OK:
            return

        time.sleep(1)

    for i in range(1):
        typ = Type.GESTURE
        message = "MOVEDOWNCATEGORY"
        if typ == Type.SPEECH:
            speech_control(youtube_music, message)
        elif typ == Type.GESTURE:
            gesture_control(youtube_music, message)
        elif typ == Type.OK:
            return

        time.sleep(1)

    for i in range(1):
        typ = Type.GESTURE
        message = "MOVELEFTCATEGORY"
        if typ == Type.SPEECH:
            speech_control(youtube_music, message)
        elif typ == Type.GESTURE:
            gesture_control(youtube_music, message)
        elif typ == Type.OK:
            return

        time.sleep(1)

    for i in range(1):
        typ = Type.GESTURE
        message = "MOVEUPCATEGORY"
        if typ == Type.SPEECH:
            speech_control(youtube_music, message)
        elif typ == Type.GESTURE:
            gesture_control(youtube_music, message)
        elif typ == Type.OK:
            return

        time.sleep(1)

    for i in range(1):
        typ = Type.GESTURE
        message = "SELECTCATEGORY"
        if typ == Type.SPEECH:
            speech_control(youtube_music, message)
        elif typ == Type.GESTURE:
            gesture_control(youtube_music, message)
        elif typ == Type.OK:
            return

        time.sleep(1) """


def speech_control(youtube_music, message):
    global intent_not_undestand_well_voice
    print(f"Speech received: {message}")

    intent = message["intent"]["name"]
    confidence = message["intent"]["confidence"]
    entities = message.get("entities", [])

    intent = "wich_music_is_playing"
    confidence = 1
    entities = [{"entity": "action", "value": "mute"}]

    if intent == "confirm_action":
        if intent_not_undestand_well_voice:
            if message["intent"]["name"] == "confirm_action":
                if (
                    message["intent"]["confidence"] > 0.7
                    and message["entities"][0]["value"] == "confirm"
                ):
                    intent = intent_not_undestand_well_voice.intent
                    entities = intent_not_undestand_well_voice.entities
                    youtube_music.sendoToTTS("Ok, vou fazer o que pediste.")
                else:
                    youtube_music.sendoToTTS("Não entendi o que disseste.")
            else:
                youtube_music.sendoToTTS("Ok, não vou fazer nada.")

            intent_not_undestand_well_voice = None
        else:
            youtube_music.sendoToTTS(random_not_understand())

    elif confidence <= 0.45:
        youtube_music.sendoToTTS(random_not_understand())
        return
    elif confidence > 0.45 and confidence < 0.8:
        intent_not_undestand_well_voice = IntentNotUnderstoodWellVoice(intent, entities)
        youtube_music.sendoToTTS(intent_not_undestand_well_voice.confirmation())
        return

    if intent == "control_music":  # DONE
        # Pausar ou continuar
        action = next((e["value"] for e in entities if e["entity"] == "action"), None)
        if action == "pause":
            youtube_music.pause()
        elif action == "resume":
            youtube_music.resume()
        else:
            youtube_music.sendoToTTS(
                "Não percebi se queres pausar ou continuar a música."
            )

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
            youtube_music.sendoToTTS(
                "Não percebi se queres passar para a póxima música, ir para a anterior ou repetir esta música."
            )

    elif intent == "adjust_volume":  # DONE
        action = next((e["value"] for e in entities if e["entity"] == "action"), None)
        if action == "increase":
            youtube_music.increase_volume_generic(10)
        elif action == "decrease":
            youtube_music.decrease_volume_generic(10)
        elif action == "mute":
            youtube_music.mute()
        elif action == "unmute":
            youtube_music.unmute()
        else:
            youtube_music.sendoToTTS(
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
            youtube_music.sendoToTTS("Não percebi qual o modo queres colocar.")

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
                youtube_music.sendoToTTS("Não percebi o nome nem o artista.")
            elif not song:
                youtube_music.sendoToTTS("Não percebi o nome da música.")
            elif not artist:
                youtube_music.sendoToTTS("Não percebi o nome do artista.")

    elif intent == "add_music_to_queue":  # DONE
        song = next((e["value"] for e in entities if e["entity"] == "song"), None)
        artist = next((e["value"] for e in entities if e["entity"] == "artist"), None)

        if song and artist:
            youtube_music.search_music(song, artist)
            youtube_music.add_to_queue()
        else:
            if not song and not artist:
                youtube_music.sendoToTTS("Não percebi o nome nem o artista.")
            elif not song:
                youtube_music.sendoToTTS("Não percebi o nome da música.")
            elif not artist:
                youtube_music.sendoToTTS("Não percebi o nome do artista.")

    elif intent == "wich_music_is_playing":  # DONE
        youtube_music.get_current_music()

    elif intent == "play_playlist":  # DONE
        playlist = next(
            (e["value"] for e in entities if e["entity"] == "playlist"), None
        )

        if playlist:
            youtube_music.play_playlist(playlist)
        else:
            youtube_music.sendoToTTS("Não percebi o nome da playlist.")

    elif intent == "add_music_to_playlist_search":  # DONE
        song = next((e["value"] for e in entities if e["entity"] == "song"), None)
        artist = next((e["value"] for e in entities if e["entity"] == "artist"), None)
        playlist = next(
            (e["value"] for e in entities if e["entity"] == "playlist"), None
        )

        if song and artist and playlist:
            youtube_music.search_music(song, artist)
            youtube_music.add_music_to_playlist_search(playlist)
        else:
            if not song and not artist and not playlist:
                youtube_music.sendoToTTS(
                    "Não percebi o nome da música, do artista e da playlist."
                )
            elif not song and not artist:
                youtube_music.sendoToTTS("Não percebi o nome da música e do artista.")
            elif not song and not playlist:
                youtube_music.sendoToTTS("Não percebi o nome da música e da playlist.")
            elif not artist and not playlist:
                youtube_music.sendoToTTS("Não percebi o nome do artista e da playlist.")
            elif not song:
                youtube_music.sendoToTTS("Não percebi o nome da música.")
            elif not artist:
                youtube_music.sendoToTTS("Não percebi o nome do artista.")
            elif not playlist:
                youtube_music.sendoToTTS("Não percebi o nome da playlist.")

    elif intent == "help":  # DONE
        option = next(
            (e["value"] for e in entities if e["entity"] == "help_option"), None
        )

        if option:
            youtube_music.help(option)
        else:
            youtube_music.help(None)

    elif intent == "goodbye":  # DONE
        youtube_music.sendoToTTS(random_goodbye())
        youtube_music.close()
        global not_quit
        not_quit = False

    else:
        youtube_music.sendoToTTS(random_not_understand())


def gesture_control(youtube_music, message):
    from youtube_music import LAST_ACTION

    print(f"Gesture received: {message}")

    if message == "HANDGOODBYE":  # Acenar com a mão para sair
        global not_quit, gesture_confirmation
        if gesture_confirmation == "HANDGOODBYE":
            not_quit = False
        else:
            gesture_confirmation = "HANDGOODBYE"
            youtube_music.sendoToTTS("Tens a certeza que queres sair?")
    elif message == "HANDMUTE":  # Fazer gesto de shiu na boca
        youtube_music.mute()
    elif message == "HANDUNMUTE":  # Apontar para a boca
        youtube_music.unmute()
    elif message == "HANDPAUSE":  # Mão aberta para a frente
        youtube_music.pause()
    elif message == "HANDRESUME":  # Girar com as mãos para a frente
        youtube_music.resume()
    elif message == "HANDNEXT":  # Deslocar mão para a direita
        youtube_music.next_song()
    elif message == "HANDPREVIOUS":  # Deslocar mão para a esquerda
        youtube_music.previous_song()
    elif message == "OPENEXPLORE":  # Abrir mãos como se fosse um livro
        youtube_music.open_explore()
    elif message == "SCROLLUPCATEGORY":  # Mão em pinça para baixo
        youtube_music.scroll_up_categories()
    elif message == "SCROLLDOWNCATEGORY":  # Mão em pinça para cima
        youtube_music.scroll_down_categories()
    elif message == "MOVEUPCATEGORY":  # Apontar para cima
        youtube_music.move_up_category()
    elif message == "MOVEDOWNCATEGORY":  # Apontar para baixo
        youtube_music.move_down_category()
    elif message == "MOVELEFTCATEGORY":  # Apontar para a esquerda
        youtube_music.move_left_category()
    elif message == "MOVERIGHTCATEGORY":  # Apontar para a direita
        youtube_music.move_right_category()
    elif message == "SELECTCATEGORY":  # Apontar e mover a mão para a frente
        if (
            LAST_ACTION == "scroll_up_categories"
            or LAST_ACTION == "scroll_down_categories"
            or LAST_ACTION == "move_down_category"
            or LAST_ACTION == "move_left_category"
            or LAST_ACTION == "move_right_category"
            or LAST_ACTION == "move_up_category"
        ):
            youtube_music.select_something_category()
        else:
            youtube_music.sendoToTTS(
                "Para selecionar algo, primeiro navega até 'Explorar'."
            )
    elif message == "HANDLIKE":  # Polegar para cima
        youtube_music.like_music()
    elif message == "HELP":  # Coçar a cabeça do lado direito
        youtube_music.help(None)


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

        youtube_music.close()
        exit(0)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
