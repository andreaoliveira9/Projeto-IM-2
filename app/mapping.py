from selenium.webdriver.common.by import By


class MapObject:
    def __init__(self, browser) -> None:
        self.browser = browser

    def find_element(self, xpath):
        return self.browser.find_element(By.XPATH, xpath)

    def find_elements(self, value):
        return self.browser.find_elements(By.XPATH, value)


class Buttons(MapObject):
    @property
    def play(self):
        return self.find_element(
            "/html/body/ytmusic-app/ytmusic-app-layout/ytmusic-player-bar/div[1]/div/tp-yt-paper-icon-button[3]/tp-yt-iron-icon"
        )

    @property
    def cookies_accept(self):
        return self.find_element(
            "//*[@id='yDmH0d']/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/form[2]/div/div/button",
        )

    @property
    def next(self):
        return self.find_element(
            "//*[@id='left-controls']/div/tp-yt-paper-icon-button[5]"
        )

    @property
    def previous(self):
        return self.find_element(
            "//*[@id='left-controls']/div/tp-yt-paper-icon-button[1]"
        )

    @property
    def volume_slider(self):
        return self.find_element("//*[@id='volume-slider'']")

    @property
    def mute(self):
        return self.find_element(
            "//*[@id='right-controls']/div/tp-yt-paper-icon-button[1]"
        )

    @property
    def repeat(self):
        return self.find_element(
            "//*[@id='right-controls']/div/tp-yt-paper-icon-button[2]"
        )

    @property
    def shuffle(self):
        return self.find_element(
            "//*[@id='right-controls']/div/tp-yt-paper-icon-button[3]"
        )

    @property
    def login(self):
        return self.find_element(
            "/html/body/ytmusic-app/ytmusic-app-layout/ytmusic-nav-bar/div[3]/a"
        )

    @property
    def next_email(self):
        return self.find_element(
            "/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[3]/div/div[1]/div/div"
        )

    @property
    def next_password(self):
        return self.find_element(
            "/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[3]/div/div[1]/div/div"
        )

    @property
    def like_music(self):
        return self.find_element(
            "/html/body/ytmusic-app/ytmusic-app-layout/ytmusic-player-bar/div[2]/div[3]/ytmusic-like-button-renderer/yt-button-shape[2]"
        )

    @property
    def first_music_play(self):
        return self.find_element(
            "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-search-page/ytmusic-tabbed-search-results-renderer/div[2]/ytmusic-section-list-renderer/div[2]/ytmusic-shelf-renderer[1]/div[3]/ytmusic-responsive-list-item-renderer[1]/div[1]/ytmusic-item-thumbnail-overlay-renderer/div/ytmusic-play-button-renderer/div"
        )

    @property
    def fisrt_music_options(self):
        return self.find_element(
            "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-search-page/ytmusic-tabbed-search-results-renderer/div[2]/ytmusic-section-list-renderer/div[2]/ytmusic-shelf-renderer[1]/div[3]/ytmusic-responsive-list-item-renderer[1]/ytmusic-menu-renderer/yt-button-shape/button"
        )

    @property
    def first_music_add_to_queue(self):
        return self.find_element(
            "/html/body/ytmusic-app/ytmusic-popup-container/tp-yt-iron-dropdown/div/ytmusic-menu-popup-renderer/tp-yt-paper-listbox/ytmusic-menu-service-item-renderer[2]"
        )

    @property
    def first_music_add_to_playlist(self):
        return self.find_element(
            "/html/body/ytmusic-app/ytmusic-popup-container/tp-yt-iron-dropdown/div/ytmusic-menu-popup-renderer/tp-yt-paper-listbox/ytmusic-menu-navigation-item-renderer[2]"
        )

    @property
    def library_tab(self):
        return self.find_element(
            "/html/body/ytmusic-app/ytmusic-app-layout/tp-yt-app-drawer/div[2]/div/div[2]/ytmusic-guide-renderer/div[2]/ytmusic-guide-section-renderer[1]/div[2]/ytmusic-guide-entry-renderer[3]/tp-yt-paper-item"
        )

    @property
    def playlists(self):
        return self.find_element(
            "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/ytmusic-section-list-renderer/div[2]/ytmusic-grid-renderer/div[2]"
        )

    @property
    def music_controls_music_name(self):
        return self.find_element(
            "/html/body/ytmusic-app/ytmusic-app-layout/ytmusic-player-bar/div[2]/div[2]/span/span[2]/yt-formatted-string/a[2]"
        )

    @property
    def music_controls_artist_name(self):
        return self.find_element(
            "/html/body/ytmusic-app/ytmusic-app-layout/ytmusic-player-bar/div[2]/div[2]/span/span[2]/yt-formatted-string/a[1]"
        )

    @property
    def choose_playlist_list(self):
        return self.find_element(
            "/html/body/ytmusic-app/ytmusic-popup-container/tp-yt-paper-dialog/ytmusic-add-to-playlist-renderer/div[2]/div[2]"
        )

    @property
    def play_playlist(self):
        return self.find_element(
            "/html/body/ytmusic-app/ytmusic-app-layout/div[4]/ytmusic-browse-response/div[2]/div[4]/div[1]/ytmusic-two-column-browse-results-renderer/div[1]/ytmusic-section-list-renderer/div[2]/ytmusic-editable-playlist-detail-header-renderer/ytmusic-responsive-header-renderer/div[6]/ytmusic-play-button-renderer/div/yt-icon"
        )


class Inputs(MapObject):
    @property
    def search(self):
        return self.find_element(
            "/html/body/ytmusic-app/ytmusic-app-layout/ytmusic-nav-bar/div[2]/ytmusic-search-box/div/div[1]/input"
        )

    @property
    def email(self):
        return self.find_element(
            "/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[2]/div/div/div[1]/form/span/section/div/div/div[1]/div/div[1]/div/div[1]/input"
        )

    @property
    def password(self):
        return self.find_element(
            "/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[2]/div/div/div/form/span/section[2]/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input"
        )
