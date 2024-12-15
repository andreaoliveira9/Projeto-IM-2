from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from difflib import SequenceMatcher
import time
import os
from dotenv import load_dotenv

from utils import *
from mapping import Buttons, Inputs
import logging

# Configure logging
logging.basicConfig(filename='play.log', level=logging.INFO, format='%(asctime)s - %(message)s')

LAST_ACTION = None

manual_login = False
try:
    options = Options()
    user_data_dir = r"C:\Users\andre\AppData\Local\Google\Chrome\User Data"
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--profile-directory=Profile 3")

    browser = webdriver.Chrome(options=options)
    browser.get("https://music.youtube.com/")
except Exception as e:
    manual_login = True
    load_dotenv(".env")

    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")

    if not EMAIL or not PASSWORD:
        print("Credenciais YouTube Music")
        EMAIL = input("Email: ")
        PASSWORD = input("Senha: ")

explore_categories = [
    "Novos álbuns e singles",
    "Disposição e géneros",
    "Tendências",
    "Novos vídeos de música",
]


class YoutubeMusic:
    def __init__(self, TTS) -> None:
        try:
            if not manual_login:
                self.browser = browser
            else:
                self.browser = uc.Chrome()
                self.browser.get("https://music.youtube.com/")
                self.browser.maximize_window()
            self.muted = False
            self.shuffled = False
            self.paused = False
            self.music_playing = True
            self.repeat = 0
            self.explore_selected = None
            self.selected = -1
            self.button_selected = None
            self.tts_func = TTS
            self.tts = TTS
            self.button = Buttons(self.browser)
            self.input = Inputs(self.browser)
            self.wait = WebDriverWait(self.browser, 20)
            self.current_selected_category = None

            if manual_login:
                self.perform_login()

            self.tts(
                "Bem-vindo ao YouTube Music, onde você pode ouvir suas músicas favoritas!"
            )

        except Exception as e:
            self.tts("Não foi possível iniciar o YouTube Music.")
            print(f"Erro: {e}")
            self.close()

    def sendoToTTS(self, message):
        actual_volume = self.actual_volume()

        volume_change = 0
        if actual_volume > 10 and self.music_playing and not self.paused:
            volume_change = actual_volume - 10
            self.decrease_volume_generic(volume_change)

        try:
            self.tts(message)
            time.sleep(
                len(message) * 0.07
            )  # Simula o tempo de fala baseado no comprimento
        finally:
            if actual_volume > 10 and self.music_playing:
                self.increase_volume_generic(volume_change)

    def perform_login(self):
        try:
            # Aceitar cookies
            cookies_accept_button = self.wait.until(
                EC.element_to_be_clickable(self.button.cookies_accept)
            )
            cookies_accept_button.click()

            # Clicar no botão de login
            login_button = self.wait.until(
                EC.element_to_be_clickable(self.button.login)
            )
            login_button.click()

            # Inserir email
            email_input = self.wait.until(EC.element_to_be_clickable(self.input.email))
            email_input.send_keys(EMAIL)
            next_email_button = self.wait.until(
                EC.element_to_be_clickable(self.button.next_email)
            )
            next_email_button.click()

            time.sleep(5)
            # Inserir senha
            password_input = self.wait.until(
                EC.element_to_be_clickable(self.input.password)
            )
            password_input.send_keys(PASSWORD)
            next_password_button = self.wait.until(
                EC.element_to_be_clickable(self.button.next_password)
            )
            next_password_button.click()

            time.sleep(5)

        except Exception as e:
            print(f"Erro inesperado: {e}")
            self.close()

    def pause(self):
        global LAST_ACTION
        if not self.music_playing:
            self.sendoToTTS("Não há nenhuma música a tocar.")
            return

        if self.paused:
            self.sendoToTTS("A música já está pausada.")
            return

        try:
            self.button.play.click()
            self.paused = True
            LAST_ACTION = "pause"
        except:
            self.sendoToTTS("Não foi possível pausar a música.")

    def resume(self):
        global LAST_ACTION
        if not self.music_playing:
            self.sendoToTTS("Não há nenhuma música a tocar.")
            return

        if not self.paused:
            self.sendoToTTS("A música não está pausada.")
            return

        try:
            self.button.play.click()
            self.paused = False
            LAST_ACTION = "resume"
        except:
            self.sendoToTTS("Não foi possível retomar a música.")

    def next_song(self):
        global LAST_ACTION
        if not self.music_playing:
            self.sendoToTTS("Não há nenhuma música a tocar.")
            return

        try:
            self.button.next.click()
            LAST_ACTION = "next_song"
        except:
            self.sendoToTTS("Não foi possível passar para a próxima música.")

    def previous_song(self):
        global LAST_ACTION
        if not self.music_playing:
            self.sendoToTTS("Não há nenhuma música a tocar.")
            return

        try:
            self.button.previous.click()
            self.button.previous.click()
            LAST_ACTION = "previous_song"
        except:
            self.sendoToTTS("Não foi possível voltar para a música anterior.")

    def repeat_song(self):
        global LAST_ACTION
        if not self.music_playing:
            self.sendoToTTS("Não há nenhuma música a tocar.")
            return

        try:
            self.button.previous.click()
            LAST_ACTION = "repeat_song"
        except:
            self.sendoToTTS("Não foi possível repetir a música.")

    def actual_volume(self):
        slider = self.button.volume_slider

        return int(slider.get_attribute("aria-valuenow"))

    def increase_volume_generic(self, value):
        global LAST_ACTION
        if not self.music_playing:
            self.sendoToTTS("Não há nenhuma música a tocar.")
            return

        try:
            slider = self.button.volume_slider

            actual_value = self.actual_volume()
            new_volume = min(100, actual_value + value)

            self.browser.execute_script(
                """
                arguments[0].setAttribute('value', arguments[1]);
                arguments[0].setAttribute('aria-valuenow', arguments[1]);
                arguments[0].querySelector('#primaryProgress').style.transform = 'scaleX(' + (arguments[1] / 100) + ')';
                arguments[0].querySelector('#sliderKnob').style.left = arguments[1] + '%';
            """,
                slider,
                new_volume,
            )

            self.browser.execute_script(
                "arguments[0].dispatchEvent(new Event('input'));", slider
            )
            self.browser.execute_script(
                "arguments[0].dispatchEvent(new Event('change'));", slider
            )
            LAST_ACTION = "increase_volume_generic"
        except:
            self.sendoToTTS("Não foi possível aumentar o volume.")

    def decrease_volume_generic(self, value):
        global LAST_ACTION
        if not self.music_playing:
            self.sendoToTTS("Não há nenhuma música a tocar.")
            return

        try:
            slider = self.button.volume_slider

            actual_value = self.actual_volume()
            new_volume = max(0, actual_value - value)

            self.browser.execute_script(
                """
                arguments[0].setAttribute('value', arguments[1]);
                arguments[0].setAttribute('aria-valuenow', arguments[1]);
                arguments[0].querySelector('#primaryProgress').style.transform = 'scaleX(' + (arguments[1] / 100) + ')';
                arguments[0].querySelector('#sliderKnob').style.left = arguments[1] + '%';
            """,
                slider,
                new_volume,
            )

            self.browser.execute_script(
                "arguments[0].dispatchEvent(new Event('input'));", slider
            )
            self.browser.execute_script(
                "arguments[0].dispatchEvent(new Event('change'));", slider
            )
            LAST_ACTION = "decrease_volume_generic"
        except:
            self.sendoToTTS("Não foi possível diminuir o volume.")

    def mute(self):
        global LAST_ACTION
        if not self.music_playing:
            self.sendoToTTS("Não há nenhuma música a tocar.")
            return

        if self.muted:
            self.sendoToTTS("O som já está desativado.")
            return

        try:
            self.button.volume_icon.click()
            self.muted = True
            LAST_ACTION = "mute"
        except:
            self.sendoToTTS("Não foi possível desativar o som.")

    def unmute(self):
        global LAST_ACTION
        if not self.music_playing:
            self.sendoToTTS("Não há nenhuma música a tocar.")
            return

        if not self.muted:
            self.sendoToTTS("O som não está desativado.")
            return

        try:
            self.button.volume_icon.click()
            self.muted = False
            LAST_ACTION = "unmute"
        except:
            self.sendoToTTS("Não foi possível ativar o som.")

    def repeat_off(self):
        global LAST_ACTION
        if not self.music_playing:
            self.sendoToTTS("Não há nenhuma música a tocar.")
            return

        if self.repeat == 0:
            self.sendoToTTS("O modo de repetição já está desativado.")
            return

        try:
            if self.repeat == 1:
                self.button.repeat.click()

            self.button.repeat.click()
            self.repeat = 0
            self.sendoToTTS("Modo de repetição desativado.")
            LAST_ACTION = "repeat_off"
        except:
            self.sendoToTTS("Não foi possível desativar o modo de repetição.")

    def repeat_all(self):
        global LAST_ACTION
        if not self.music_playing:
            self.sendoToTTS("Não há nenhuma música a tocar.")
            return

        if self.repeat == 1:
            self.sendoToTTS("O modo de repetição de todas as músicas já está ativado.")
            return

        try:
            if self.repeat == 2:
                self.button.repeat.click()

            self.button.repeat.click()
            self.repeat = 1
            self.sendoToTTS("Modo de repetição de todas as músicas ativado.")
            LAST_ACTION = "repeat_all"
        except:
            self.sendoToTTS("Não foi possível ativar a repetição de todas as músicas.")

    def repeat_one(self):
        global LAST_ACTION
        if not self.music_playing:
            self.sendoToTTS("Não há nenhuma música a tocar.")
            return

        if self.repeat == 2:
            self.sendoToTTS("O modo de repetição de uma música já está ativado.")
            return

        try:
            if self.repeat == 0:
                self.button.repeat.click()

            self.button.repeat.click()
            self.repeat = 2
            self.sendoToTTS("Modo de repetição de uma música ativado.")
            LAST_ACTION = "repeat_one"
        except:
            self.sendoToTTS("Não foi possível ativar a repetição de uma música.")

    def shuffle_on(self):
        global LAST_ACTION
        if not self.music_playing:
            self.sendoToTTS("Não há nenhuma música a tocar.")
            return

        if self.shuffled:
            self.sendoToTTS("O modo aleatório já está ativado.")
            return

        try:
            self.button.shuffle.click()
            self.shuffled = True
            self.sendoToTTS("Modo aleatório ativado.")
            LAST_ACTION = "shuffle_on"
        except:
            self.sendoToTTS("Não foi possível ativar o modo aleatório.")

    def shuffle_off(self):
        global LAST_ACTION
        if not self.music_playing:
            self.sendoToTTS("Não há nenhuma música a tocar.")
            return

        if not self.shuffled:
            self.sendoToTTS("O modo aleatório já está desativado.")
            return

        try:
            self.button.shuffle.click()
            self.shuffled = False
            self.sendoToTTS("Modo aleatório desativado.")
            LAST_ACTION = "shuffle_off"
        except:
            self.sendoToTTS("Não foi possível desativar o modo aleatório.")

    def like_music(self):
        global LAST_ACTION
        if not self.music_playing:
            self.sendoToTTS("Não há nenhuma música a tocar.")
            return

        try:
            self.button.like_music.click()
            self.sendoToTTS("Música curtida.")
            LAST_ACTION = "like_music"
        except:
            self.sendoToTTS("Não foi possível curtir a música.")

    def search_music(self, song, artist):
        global LAST_ACTION
        self.sendoToTTS(f"Procurando por '{song}' de {artist}.")
        try:
            self.browser.get("https://music.youtube.com/")
            self.music_playing = False

            search_input = self.input.search
            search_input.clear()
            search_input.send_keys(f"{song} {artist}")
            search_input.send_keys(Keys.RETURN)

            time.sleep(1)
            LAST_ACTION = "search_music"
        except:
            self.sendoToTTS("Não foi possível encontrar a música.")

    def play_music_searched(self):
        global LAST_ACTION
        try:
            self.button.first_music_play.click()
            self.music_playing = True
            LAST_ACTION = "play_music_searched"
        except:
            self.sendoToTTS("Não foi possível tocar a música.")

    def get_current_music(self):
        global LAST_ACTION
        if not self.music_playing:
            self.sendoToTTS("Não há nenhuma música a tocar.")
            return

        try:
            music_name = self.button.music_controls_music_name.text
            artist_name = self.button.music_controls_artist_name.text

            self.sendoToTTS(f"A música atual é {music_name} de {artist_name}.")
            LAST_ACTION = "get_current_music"
        except:
            self.sendoToTTS("Não foi possível obter o nome da música atual.")

    def add_to_queue(self):
        global LAST_ACTION
        try:
            action_chain = ActionChains(self.browser)

            action_chain.move_to_element(self.button.first_music_play).click(
                self.button.fisrt_music_options
            ).perform()

            self.button.first_music_add_to_queue.click()
            self.music_playing = True
            self.sendoToTTS("Música adicionada à fila.")
            LAST_ACTION = "add_to_queue"
        except:
            self.sendoToTTS("Não foi possível adicionar a música à fila.")

    def play_playlist(self, playlist):
        global LAST_ACTION
        self.sendoToTTS(f"Procurando pela playlist {playlist}.")
        try:
            self.button.library_tab.click()

            time.sleep(1)

            container = self.button.playlists

            time.sleep(1)

            playlists = container.find_elements(
                By.XPATH,
                ".//a[@class='yt-simple-endpoint style-scope yt-formatted-string']",
            )

            if not playlists:
                self.sendoToTTS("Nenhuma playlist encontrada.")
                return None

            playlists_names = [
                element.text for element in playlists if element.text.strip()
            ]

            def similarity(a, b):
                return SequenceMatcher(None, a.lower(), b.lower()).ratio()

            closest_playlist = max(
                playlists_names, key=lambda p: similarity(playlist, p[0])
            )

            target_playlist = None
            for element in playlists:
                if element.text.strip() == closest_playlist:
                    target_playlist = element
                    break

            target_playlist.click()

            time.sleep(1)

            self.button.play_playlist.click()

            self.music_playing = True
            LAST_ACTION = "play_playlist"
        except:
            self.sendoToTTS("Não foi possível encontrar a playlist.")

    def add_music_to_playlist_search(self, playlist):
        global LAST_ACTION
        self.sendoToTTS("Adicionando a música à playlist.")
        try:
            action_chain = ActionChains(self.browser)

            action_chain.move_to_element(self.button.first_music_play).click(
                self.button.fisrt_music_options
            ).perform()

            self.button.first_music_add_to_playlist.click()

            time.sleep(1)

            container = self.button.choose_playlist_list

            time.sleep(1)

            playlists = container.find_elements(By.XPATH, "//*[@id='title']")

            if not playlists:
                self.sendoToTTS("Nenhuma playlist encontrada.")
                return None

            playlists_names = [
                element.text for element in playlists if element.text.strip()
            ]

            def similarity(a, b):
                return SequenceMatcher(None, a.lower(), b.lower()).ratio()

            closest_playlist = max(
                playlists_names, key=lambda p: similarity(playlist, p[0])
            )

            target_playlist = None
            for element in playlists:
                if element.text.strip() == closest_playlist:
                    target_playlist = element
                    break

            target_playlist.click()
            LAST_ACTION = "add_music_to_playlist_search"
        except:
            self.sendoToTTS("Não foi possível adicionar a música à playlist.")

    def open_explore(self):
        global LAST_ACTION
        try:
            self.explore_selected = 0
            self.selected = 0
            self.button.explore_tab.click()
            time.sleep(2)
            try:
                if self.explore_selected == 0:
                    container = self.browser.find_element(
                        By.XPATH,
                        "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[1]/div/ytmusic-carousel/div/ul",
                    )

                    card = container.find_elements(
                        By.CSS_SELECTOR,
                        "#items ytmusic-two-row-item-renderer",
                    )

                    self.current_selected_category = card[self.selected].find_element(By.ID, "content")
                    self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                    )
                    actions = ActionChains(self.browser)
                    actions.move_to_element(self.current_selected_category).perform()
                    self.button_selected = self.current_selected_category
            except:
                self.sendoToTTS("Não foi possível selecionar o primeiro elemento.")

            LAST_ACTION = "open_explore"
        except:
            self.sendoToTTS("Não foi possível abrir a biblioteca.")

    def scroll_up_categories(self):
        global LAST_ACTION
        self.selected = 0
        if self.browser.current_url != "https://music.youtube.com/explore":
            self.sendoToTTS("Não é possível mover para cima nesta página.")
            return

        index = self.explore_selected - 1
        if index < 0:
            self.sendoToTTS("Não há mais categorias acima.")
            return

        text_to_find = explore_categories[index]
        try:
            target_element = self.browser.find_element(
                By.XPATH, f"//a[text()='{text_to_find}']"
            )

            self.browser.execute_script(
                "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'start' });",
                target_element,
            )

            self.explore_selected = index
            if self.explore_selected == 0:
                    container = self.browser.find_element(
                        By.XPATH,
                        "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[1]/div/ytmusic-carousel/div/ul",
                    )

                    card = container.find_elements(
                        By.CSS_SELECTOR,
                        "#items ytmusic-two-row-item-renderer",
                    )

                    self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                    )

                    self.current_selected_category = card[self.selected].find_element(By.ID, "content")
                    self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                    )
                    actions = ActionChains(self.browser)
                    actions.move_to_element(self.current_selected_category).perform()
                    self.button_selected = self.current_selected_category

            elif self.explore_selected == 1:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[2]/div/ytmusic-carousel/div/ul",
                )

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-navigation-button-renderer",
                )

                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )
                self.selected = 0

                self.current_selected_category = card[self.selected].find_element(By.CSS_SELECTOR, "button")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category

            elif self.explore_selected == 2:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[3]/div/ytmusic-carousel/div/ul",
                )

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-responsive-list-item-renderer",
                )

                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )
                self.selected = 0

                self.current_selected_category = card[self.selected].find_element(By.ID, "content")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category
            elif self.explore_selected == 3:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[4]/div/ytmusic-carousel/div/ul",
                )

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-two-row-item-renderer",
                )

                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )
                self.selected = 0

                self.current_selected_category = card[self.selected].find_element(By.ID, "content")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category

            LAST_ACTION = "scroll_up_categories"
        except:
            self.sendoToTTS("Não foi possível mover para cima.")

    def scroll_down_categories(self):
        global LAST_ACTION
        self.selected = 0
        if self.browser.current_url != "https://music.youtube.com/explore":
            self.sendoToTTS("Não é possível mover para baixo nesta página.")
            return
        
        index = self.explore_selected + 1
        if index >= len(explore_categories):
            self.sendoToTTS("Não há mais categorias abaixo.")
            return

        text_to_find = explore_categories[index]
        try:
            target_element = self.browser.find_element(
                By.XPATH, f"//a[text()='{text_to_find}']"
            )

            self.browser.execute_script(
                "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'start' });",
                target_element,
            )

            self.explore_selected = index
            if self.explore_selected == 0:
                    container = self.browser.find_element(
                        By.XPATH,
                        "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[1]/div/ytmusic-carousel/div/ul",
                    )

                    card = container.find_elements(
                        By.CSS_SELECTOR,
                        "#items ytmusic-two-row-item-renderer",
                    )

                    self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                    )

                    self.current_selected_category = card[self.selected].find_element(By.ID, "content")
                    self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                    )
                    actions = ActionChains(self.browser)
                    actions.move_to_element(self.current_selected_category).perform()
                    self.button_selected = self.current_selected_category

            elif self.explore_selected == 1:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[2]/div/ytmusic-carousel/div/ul",
                )

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-navigation-button-renderer",
                )

                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )
                self.selected = 0

                self.current_selected_category = card[self.selected].find_element(By.CSS_SELECTOR, "button")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category

            elif self.explore_selected == 2:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[3]/div/ytmusic-carousel/div/ul",
                )

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-responsive-list-item-renderer",
                )

                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )
                self.selected = 0

                self.current_selected_category = card[self.selected].find_element(By.ID, "content")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category
            elif self.explore_selected == 3:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[4]/div/ytmusic-carousel/div/ul",
                )

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-two-row-item-renderer",
                )

                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )
                self.selected = 0

                self.current_selected_category = card[self.selected].find_element(By.ID, "content")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category

            LAST_ACTION = "scroll_down_categories"
        except:
            self.sendoToTTS("Não foi possível mover para baixo.")

    def move_right_category(self):
        global LAST_ACTION
        if self.browser.current_url != "https://music.youtube.com/explore":
            self.sendoToTTS("Não é possível mover para a direita nesta página.")
            return

        try:
            if self.explore_selected == 0:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[1]/div/ytmusic-carousel/div/ul",
                )
                

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-two-row-item-renderer",
                )

                if self.selected + 1 > len(card) - 1:
                    self.sendoToTTS("Não há mais opções à direita.")
                    return
                
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )

                self.selected += 1

                self.current_selected_category = card[self.selected].find_element(By.ID, "content")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category

            elif self.explore_selected == 1:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[2]/div/ytmusic-carousel/div/ul",
                )

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-navigation-button-renderer",
                )

                if self.selected + 4 > len(card) - 1:
                    self.sendoToTTS("Não há mais opções à direita.")
                    return

                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )
                self.selected += 4

                self.current_selected_category = card[self.selected].find_element(By.CSS_SELECTOR, "button")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category

            elif self.explore_selected == 2:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[3]/div/ytmusic-carousel/div/ul",
                )

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-responsive-list-item-renderer",
                )

                if self.selected + 4 > len(card) - 1:
                    print("Não há mais opções à direita.")
                    self.sendoToTTS("Não há mais opções à direita.")
                    return

                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )
                self.selected += 4

                self.current_selected_category = card[self.selected].find_element(By.ID, "content")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category

            elif self.explore_selected == 3:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[4]/div/ytmusic-carousel/div/ul",
                )

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-two-row-item-renderer",
                )

                if self.selected + 1 > len(card) - 1:
                    self.sendoToTTS("Não há mais opções à direita.")
                    return

                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )
                self.selected += 1

                self.current_selected_category = card[self.selected].find_element(By.ID, "content")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category

            LAST_ACTION = "move_right_category"
        except:
            self.sendoToTTS("Não foi possível mover para a direita.")

    def move_left_category(self):
        global LAST_ACTION
        if self.browser.current_url != "https://music.youtube.com/explore":
            self.sendoToTTS("Não é possível mover para a esquerda nesta página.")
            return

        try:
            if self.explore_selected == 0:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[1]/div/ytmusic-carousel/div/ul",
                )

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-two-row-item-renderer",
                )

                if self.selected - 1 < 0:
                    self.sendoToTTS("Não há mais opções à esquerda.")
                    return

                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )
                self.selected -= 1

                self.current_selected_category = card[self.selected].find_element(By.ID, "content")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category

            elif self.explore_selected == 1:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[2]/div/ytmusic-carousel/div/ul",
                )

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-navigation-button-renderer",
                )

                if self.selected - 4 < 0:
                    self.sendoToTTS("Não há mais opções à esquerda.")
                    return

                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )
                self.selected -= 4

                self.current_selected_category = card[self.selected].find_element(By.CSS_SELECTOR, "button")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category

            elif self.explore_selected == 2:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[3]/div/ytmusic-carousel/div/ul",
                )

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-responsive-list-item-renderer",
                )

                if self.selected - 4 < 0:
                    self.sendoToTTS("Não há mais opções à esquerda.")
                    return

                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )
                self.selected -= 4

                self.current_selected_category = card[self.selected].find_element(By.ID, "content")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category

            elif self.explore_selected == 3:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[4]/div/ytmusic-carousel/div/ul",
                )

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-two-row-item-renderer",
                )

                if self.selected - 1 < 0:
                    self.sendoToTTS("Não há mais opções à esquerda.")
                    return
                
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )
                self.selected -= 1

                self.current_selected_category = card[self.selected].find_element(By.ID, "content")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category

            LAST_ACTION = "move_left_category"
        except:
            self.sendoToTTS("Não foi possível mover para a esquerda.")

    def move_down_category(self):
        global LAST_ACTION
        if self.browser.current_url != "https://music.youtube.com/explore":
            self.sendoToTTS("Não é possível mover para baixo nesta página.")
            return

        try:
            if self.explore_selected == 0 or self.explore_selected == 3:
                self.sendoToTTS("Não há opções abaixo.")
                return

            elif self.explore_selected == 1:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[2]/div/ytmusic-carousel/div/ul",
                )

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-navigation-button-renderer",
                )

                if (self.selected + 1) % 4 == 0:
                    self.sendoToTTS("Não há mais opções abaixo.")
                    return

                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )
                self.selected += 1

                self.current_selected_category = card[self.selected].find_element(By.CSS_SELECTOR, "button")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category

            elif self.explore_selected == 2:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[3]/div/ytmusic-carousel/div/ul",
                )

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-responsive-list-item-renderer",
                )

                if (self.selected + 1) % 4 == 0:
                    self.sendoToTTS("Não há mais opções abaixo.")
                    return

                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )
                self.selected += 1

                self.current_selected_category = card[self.selected].find_element(By.ID, "content")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category

            LAST_ACTION = "move_down_category"
        except:
            self.sendoToTTS("Não foi possível mover para baixo.")

    def move_up_category(self):
        global LAST_ACTION
        if self.browser.current_url != "https://music.youtube.com/explore":
            self.sendoToTTS("Não é possível mover para cima nesta página.")
            return

        try:
            if self.explore_selected == 0 or self.explore_selected == 3:
                self.sendoToTTS("Não há opções acima.")
                return

            elif self.explore_selected == 1:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[2]/div/ytmusic-carousel/div/ul",
                )

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-navigation-button-renderer",
                )

                if self.selected - 4 < 0:
                    self.sendoToTTS("Não há mais opções acima.")
                    return

                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )
                self.selected -= 1

                self.current_selected_category = card[self.selected].find_element(By.CSS_SELECTOR, "button")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category

            elif self.explore_selected == 2:
                container = self.browser.find_element(
                    By.XPATH,
                    "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-carousel-shelf-renderer[3]/div/ytmusic-carousel/div/ul",
                )

                card = container.find_elements(
                    By.CSS_SELECTOR,
                    "#items ytmusic-responsive-list-item-renderer",
                )

                if self.selected - 4 < 0:
                    self.sendoToTTS("Não há mais opções acima.")
                    return

                self.browser.execute_script(
                        """
                        arguments[0].style.border = '';
                        """, self.current_selected_category
                )
                
                self.selected -= 1

                self.current_selected_category = card[self.selected].find_element(By.ID, "content")
                self.browser.execute_script(
                        """
                        arguments[0].style.border = '2px solid red';
                        """, self.current_selected_category
                )

                actions = ActionChains(self.browser)
                actions.move_to_element(self.current_selected_category).perform()
                self.button_selected = self.current_selected_category

            LAST_ACTION = "move_up_category"
        except:
            self.sendoToTTS("Não foi possível mover para cima.")

    def select_something_category(self):
        global LAST_ACTION
        try:
            self.button_selected.click()
            LAST_ACTION = "select_something_category"
        except:
            self.sendoToTTS("Não foi possível selecionar a opção.")
    
    def play_music_by_link(self):
        global LAST_ACTION
        try:
            # Get a random music link
            link = random_music()

            # Open the specified link in the browser
            self.browser.get(link)

            # Set music_playing to True and update LAST_ACTION
            self.music_playing = True
            LAST_ACTION = "play_music_by_link"

        except Exception as e:
            print(f"Error playing music by link: {e}")
            self.sendoToTTS("Não foi possível reproduzir a música.")

    def help(self, option):
        global LAST_ACTION
        if option:
            if option == "todas" or option == "pesquisar uma música":
                self.sendoToTTS(
                    "Para pesquisar uma música, diga, por exemplo, 'Põe a tocar a música Shape of You do cantor Ed Sheeran.'."
                )
            if option == "todas" or option == "tocar uma playlist":
                self.sendoToTTS(
                    "Para tocar uma playlist, diga, por exemplo, 'Quero ouvir a playlist de Pop.'."
                )
            if option == "todas" or option == "controlar a música":
                self.sendoToTTS(
                    "Para pausar a música, diga, por exemplo, 'Pausa a musica.'. Para retomar a música, diga, por exemplo, 'Continua a tocar a música.'."
                )
            if option == "todas" or option == "mudar de música":
                self.sendoToTTS(
                    "Para avançar de música, diga, por exemplo, 'Próxima faixa.'. Para voltar para a música anterior, diga, por exemplo, 'Música anterior.'. Para repetir a música, diga, por exemplo, 'Repetir música.'."
                )
            if option == "todas" or option == "ajustar o volume":
                self.sendoToTTS(
                    "Para aumentar o volume, diga, por exemplo, 'Aumentar o volume.'. Para diminuir o volume, diga, por exemplo, 'Diminuir o volume.'. Para ativar o som, diga, por exemplo, 'Ativa o som.'. Para desativar o som, diga, por exemplo, 'Desativa o som.'."
                )
            if option == "todas" or option == "mudar o modo":
                self.sendoToTTS(
                    "Para ativar o modo aleatório, diga, por exemplo, 'Podes misturar as músicas?'. Para desativar o modo aleatório, diga, por exemplo, 'Desativar o modo aleatório.'. Para ativar o modo de repetição de uma música, diga, por exemplo, 'Repete a mesma música por favor.'. Para ativar o modo de repetição de todas as músicas, diga, por exemplo, 'Repete este conjunto de músicas por favor.'. Para desativar o modo de repetição, diga, por exemplo, 'Desativa o modo de repetição.'."
                )
            if option == "todas" or option == "adicionar aos favoritos":
                self.sendoToTTS(
                    "Para adicionar a música aos favoritos, diga, por exemplo, 'Dá like na musica.'."
                )
            if option == "todas" or option == "confirmar açao":
                self.sendoToTTS("Para confirmar a ação, diga, por exemplo, 'Sim'.")
            if option == "todas" or option == "adicionar à fila":
                self.sendoToTTS(
                    "Para adicionar a música à fila, diga, por exemplo, 'Põe a tocar a música Shape of You do cantor Ed Sheeran a seguir.'."
                )
            if option == "todas" or option == "saber que música esta a tocar":
                self.sendoToTTS(
                    "Para saber que música está a tocar, diga, por exemplo, 'Que música está a tocar?'."
                )
            if option == "todas" or option == "adicionar à playlist":
                self.sendoToTTS(
                    "Para adicionar a música à playlist, diga, por exemplo, 'Adiciona a música Someone Like You da cantora Adele à playlist de Pop.'."
                )
            if option == "todas" or option == "sair da aplicação":
                self.sendoToTTS(
                    "Para sair da aplicação, diga, por exemplo, 'Quero fechar a aplicação, adeus.'."
                )
        else:
            self.sendoToTTS(
                "Podes pedir para pesquisar uma música, tocar uma playlist, controlar a música, mudar de música, ajustar o volume, mudar o modo, adicionar aos favoritos, confirmar a ação, adicionar à fila, saber que música está a tocar, adicionar à playlist e sair da aplicação."
            )

        LAST_ACTION = "help"

    def close(self):
        self.browser.close()
