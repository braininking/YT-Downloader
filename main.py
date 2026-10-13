import os, threading, re
from pathlib import Path
from urllib.parse import urlparse
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Rectangle
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label

KV = r"""
#:import dp kivy.metrics.dp
<NeonButton@Button>:
    background_normal: ''
    background_down: ''
    background_color: (0.45,0.20,1,1) if self.state == 'normal' else (0.15,0.75,1,1)
    color: 1,1,1,1
    bold: True
    size_hint_y: None
    height: dp(48)
<NeonSpinner@Spinner>:
    background_normal: ''
    background_color: .12,.10,.22,.96
    color: 1,1,1,1
    size_hint_y: None
    height: dp(46)
<Root>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: .025,.015,.06,1
        Rectangle:
            pos: self.pos
            size: self.size
    ScrollView:
        do_scroll_x: False
        BoxLayout:
            orientation: 'vertical'
            padding: dp(18), dp(22)
            spacing: dp(13)
            size_hint_y: None
            height: self.minimum_height
            canvas.before:
                Color:
                    rgba: .025,.015,.06,.90
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: '[b]YT [color=\"#9B5CFF\"]DOWNLOADER[/color][/b]'
                markup: True
                font_size: '25sp'
                size_hint_y: None
                height: dp(44)
            Label:
                text: 'VÃDEOS E ÃUDIO â€¢ ANDROID'
                color: .15,.82,1,1
                font_size: '11sp'
                size_hint_y: None
                height: dp(22)
            Label:
                text: 'Cole o link do conteÃºdo que vocÃª tem autorizaÃ§Ã£o para baixar.'
                color: .78,.75,.88,1
                halign: 'left'
                text_size: self.width, None
                size_hint_y: None
                height: self.texture_size[1] + dp(8)
            TextInput:
                id: url
                hint_text: 'https://...'
                multiline: False
                size_hint_y: None
                height: dp(50)
                background_normal: ''
                background_active: ''
                background_color: .10,.08,.18,1
                foreground_color: 1,1,1,1
                cursor_color: .1,.8,1,1
                padding: dp(12), dp(14)
            Label:
                text: 'TIPO'
                color: .18,.82,1,1
                halign: 'left'
                size_hint_y: None
                height: dp(22)
            Spinner:
                id: kind
                text: 'VÃ­deo'
                values: ['VÃ­deo','Ãudio']
                background_normal: ''
                background_color: .12,.10,.22,1
                color: 1,1,1,1
                size_hint_y: None
                height: dp(46)
            Label:
                text: 'FORMATO'
                color: .18,.82,1,1
                halign: 'left'
                size_hint_y: None
                height: dp(22)
            Spinner:
                id: fmt
                text: 'MP4'
                values: ['MP4','MKV','WEBM','MP3','M4A','OPUS']
                background_normal: ''
                background_color: .12,.10,.22,1
                color: 1,1,1,1
                size_hint_y: None
                height: dp(46)
            Label:
                text: 'QUALIDADE'
                color: .18,.82,1,1
                halign: 'left'
                size_hint_y: None
                height: dp(22)
            Spinner:
                id: quality
                text: 'Melhor disponÃ­vel'
                values: ['Melhor disponÃ­vel','8K / 4320p','4K / 2160p','1440p','1080p','720p','480p','360p','240p','144p']
                background_normal: ''
                background_color: .12,.10,.22,1
                color: 1,1,1,1
                size_hint_y: None
                height: dp(46)
            BoxLayout:
                size_hint_y: None
                height: dp(36)
                CheckBox:
                    id: playlist
                    size_hint_x: None
                    width: dp(42)
                    color: .1,.8,1,1
                Label:
                    text: 'Baixar playlist inteira'
                    color: .9,.88,1,1
                    halign: 'left'
            NeonButton:
                text: 'â¬‡  BAIXAR AGORA'
                on_release: app.start_download()
            NeonButton:
                text: 'CANCELAR DOWNLOAD'
                background_color: .24,.12,.38,1
                on_release: app.cancel_download()
            ProgressBar:
                id: progress
                max: 100
                value: app.progress
                size_hint_y: None
                height: dp(10)
            Label:
                text: str(int(app.progress)) + '%'
                color: .15,.82,1,1
                size_hint_y: None
                height: dp(24)
            Label:
                text: app.status
                color: .9,.86,1,1
                halign: 'left'
                text_size: self.width, None
                size_hint_y: None
                height: max(dp(42), self.texture_size[1] + dp(10))
            Label:
                text: 'PRETO â€¢ ROXO NEON â€¢ AZUL ELÃ‰TRICO â€¢ CIANO'
                color: .65,.53,.9,1
                font_size: '10sp'
                size_hint_y: None
                height: dp(24)
"""
class Root(BoxLayout):
    pass

class YTDownloaderAndroid(App):
    status = StringProperty('Pronto para baixar.')
    progress = NumericProperty(0)
    cancel_flag = False

    def build(self):
        self.title = 'YT Downloader'
        Window.clearcolor = (.025,.015,.06,1)
        try:
            self.wallpaper_texture = CoreImage(os.path.join(os.path.dirname(__file__), 'wallpaper.png')).texture
        except Exception:
            self.wallpaper_texture = None
        Builder.load_string(KV)
        root = Root()
        self.root_ref = root
        self._download_dir = self._get_download_dir()
        return root

    def _get_download_dir(self):
        if platform == 'android':
            try:
                from android.storage import primary_external_storage_path
                return os.path.join(primary_external_storage_path(), 'Download', 'YT Downloader')
            except Exception:
                pass
        return str(Path.home() / 'Downloads' / 'YT Downloader')

    def _show(self, text):
        self.status = text

    def start_download(self):
        u = self.root_ref.ids.url.text.strip()
        if not u or not urlparse(u).scheme or not urlparse(u).netloc:
            self.status = 'Cole um link vÃ¡lido primeiro.'
            return
        self.cancel_flag = False
        self.progress = 0
        self.status = 'Preparando downloadâ€¦'
        threading.Thread(target=self._download, args=(u,), daemon=True).start()

    def cancel_download(self):
        self.cancel_flag = True
        self.status = 'Solicitando cancelamentoâ€¦'

    def _download(self, url):
        try:
            import yt_dlp
            from yt_dlp.utils import DownloadError
            os.makedirs(self._download_dir, exist_ok=True)
            root = self.root_ref
            audio = root.ids.kind.text == 'Ãudio'
            fmt = root.ids.fmt.text.upper()
            q = root.ids.quality.text
            height = {'8K / 4320p':4320,'4K / 2160p':2160,'1440p':1440,'1080p':1080,'720p':720,'480p':480,'360p':360,'240p':240,'144p':144}.get(q)
            def hook(d):
                if self.cancel_flag:
                    raise DownloadError('Cancelado pelo usuÃ¡rio')
                if d.get('status') == 'downloading':
                    total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                    done = d.get('downloaded_bytes', 0)
                    p = done * 100 / total if total else 0
                    Clock.schedule_once(lambda dt: setattr(self, 'progress', p))
                    speed = d.get('speed')
                    eta = d.get('eta')
                    msg = f"Baixandoâ€¦ {p:.1f}%"
                    if speed: msg += f" â€¢ {speed/1024/1024:.1f} MB/s"
                    if eta is not None: msg += f" â€¢ faltam {eta}s"
                    Clock.schedule_once(lambda dt, m=msg: self._show(m))
                elif d.get('status') == 'finished':
                    Clock.schedule_once(lambda dt: setattr(self, 'progress', 100))
                    Clock.schedule_once(lambda dt: self._show('Processando arquivoâ€¦'))
            opts = {'outtmpl': os.path.join(self._download_dir, '%(title).180B [%(id)s].%(ext)s'),
                    'noplaylist': not root.ids.playlist.active, 'progress_hooks':[hook],
                    'retries': 5, 'fragment_retries': 5, 'continuedl': True,
                    'windowsfilenames': False, 'quiet': True, 'no_warnings': True}
            if audio:
                opts['format'] = 'bestaudio/best'
                if fmt in ('MP3','M4A','OPUS'):
                    codec = {'MP3':'mp3','M4A':'m4a','OPUS':'opus'}[fmt]
                    opts['postprocessors'] = [{'key':'FFmpegExtractAudio','preferredcodec':codec,
                                               'preferredquality':'320' if q == 'Melhor disponÃ­vel' else '192'}]
            else:
                opts['format'] = (f'bestvideo[height<={height}]+bestaudio/best[height<={height}]/best' if height
                                  else 'bestvideo+bestaudio/best')
                if fmt in ('MP4','MKV'):
                    opts['merge_output_format'] = fmt.lower()
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            Clock.schedule_once(lambda dt: self._finish('Download concluÃ­do! Confira a pasta Download/YT Downloader.'))
        except Exception as e:
            msg = str(e)
            if self.cancel_flag: msg = 'Download cancelado.'
            else: msg = 'Falha no download: ' + msg[:240]
            Clock.schedule_once(lambda dt, m=msg: self._finish(m))
    def _finish(self, msg):
        self.status = msg

if __name__ == '__main__':
    YTDownloaderAndroid().run()

