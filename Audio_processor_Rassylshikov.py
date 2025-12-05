import wave
import struct
import math
import os


class AudioProcessor:
    """Класс для обработки WAV аудиофайлов без внешних зависимостей"""

    def __init__(self, file_path):
        """
        Инициализация процессора аудио

        Args:
            file_path (str): Путь к WAV файлу
        """
        self.file_path = file_path
        self.load_wav(file_path)
        self.original_duration = self.get_duration()

    def load_wav(self, file_path):
        """Загрузка WAV файла"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension != '.wav':
            raise ValueError("Поддерживаются только WAV файлы!")

        with wave.open(file_path, 'rb') as wav_file:
            self.channels = wav_file.getnchannels()
            self.sample_width = wav_file.getsampwidth()
            self.frame_rate = wav_file.getframerate()
            self.n_frames = wav_file.getnframes()
            self.frames = wav_file.readframes(self.n_frames)

    def get_duration(self):
        """Получить длительность в секундах"""
        return self.n_frames / float(self.frame_rate)

    def get_channels(self):
        """Получить количество каналов (1=моно, 2=стерео)"""
        return self.channels

    def get_sample_rate(self):
        """Получить частоту дискретизации в Гц"""
        return self.frame_rate

    def trim(self, start_sec, end_sec):
        """
        Обрезка аудио

        Args:
            start_sec (float): Начало в секундах
            end_sec (float): Конец в секундах
        """
        if start_sec < 0:
            raise ValueError("Начало не может быть отрицательным")
        if end_sec <= start_sec:
            raise ValueError("Конец должен быть больше начала")

        duration = self.get_duration()
        if start_sec > duration:
            raise ValueError(f"Начало ({start_sec}с) превышает длительность ({duration:.2f}с)")

        # Ограничиваем end_sec длительностью файла
        end_sec = min(end_sec, duration)

        start_frame = int(start_sec * self.frame_rate)
        end_frame = int(end_sec * self.frame_rate)

        bytes_per_frame = self.sample_width * self.channels
        start_byte = start_frame * bytes_per_frame
        end_byte = end_frame * bytes_per_frame

        self.frames = self.frames[start_byte:end_byte]
        self.n_frames = end_frame - start_frame

    def change_volume(self, db_change):
        """
        Изменение громкости

        Args:
            db_change (float): Изменение в децибелах (+10 = громче, -10 = тише)
        """
        # Коэффициент изменения громкости
        factor = math.pow(10, db_change / 20.0)

        # Определяем формат данных
        fmt_map = {1: 'b', 2: 'h', 4: 'i'}
        if self.sample_width not in fmt_map:
            raise ValueError(f"Неподдерживаемая ширина сэмпла: {self.sample_width}")

        fmt = fmt_map[self.sample_width]
        num_samples = len(self.frames) // self.sample_width

        # Распаковываем байты в список значений
        samples = list(struct.unpack(f'{num_samples}{fmt}', self.frames))

        # Максимальное значение для данной разрядности
        max_val = 2 ** (8 * self.sample_width - 1) - 1
        min_val = -max_val - 1

        # Применяем изменение громкости с ограничением
        samples = [int(max(min(s * factor, max_val), min_val)) for s in samples]

        # Упаковываем обратно в байты
        self.frames = struct.pack(f'{len(samples)}{fmt}', *samples)

    def save(self, output_path):
        """
        Сохранение аудио в WAV файл

        Args:
            output_path (str): Путь для сохранения
        """
        file_extension = os.path.splitext(output_path)[1].lower()
        if file_extension != '.wav':
            output_path += '.wav'

        with wave.open(output_path, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(self.sample_width)
            wav_file.setframerate(self.frame_rate)
            wav_file.writeframes(self.frames)

    def get_audio_info(self):
        """Получить информацию об аудио"""
        return {
            'duration': self.get_duration(),
            'channels': self.get_channels(),
            'sample_rate': self.get_sample_rate(),
            'sample_width': self.sample_width,
            'bit_depth': self.sample_width * 8,
            'original_duration': self.original_duration
        }
