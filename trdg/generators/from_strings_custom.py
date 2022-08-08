import random
from pathlib import Path
from typing import Tuple, Union, List, Optional

from trdg.data_generator import FakeTextDataGenerator
from trdg.generators import GeneratorFromStrings
from trdg.utils import load_fonts


class GeneratorFromStringsCustom(GeneratorFromStrings):  # TODO: maybe different name

    def __init__(
            self,
            *args,
            strings: Tuple[str],
            font_dir: Path = None,
            shearing_angle: Union[int, List[int]] = 0,
            space_width: Union[float, List[float]] = 1.0,
            character_spacing: int = 0,
            margins: Tuple[int, int, int, int] = (0, 0, 0, 0),
            color: Union[str, List[str]] = "#282828",
            word_pos_variance: Optional[Tuple[float, float]] = None,
            **kwargs
    ):
        count = len(strings)
        fonts = load_fonts(font_dir)
        self.shearing_angle = shearing_angle
        self.color = color
        self.word_pos_variance = word_pos_variance
        super().__init__(*args, strings=strings, count=count, fonts=fonts, space_width=space_width,
                         character_spacing=character_spacing, margins=margins, **kwargs)

    @staticmethod
    def get_int_in_interval(interval) -> int:
        if isinstance(interval, int):
            interval_start = 0
            interval_end = interval
        elif isinstance(interval, list):
            interval_start, interval_end = interval
        else:
            raise ValueError("Given value must be int or tuple")
        return random.randint(interval_start, interval_end)

    def get_space_width(self) -> float:
        if isinstance(self.space_width, float):
            return self.space_width
        elif isinstance(self.space_width, list):
            interval_start, interval_end = self.space_width
        else:
            raise ValueError("Space_width must be float or tuple of floats")
        return random.uniform(interval_start, interval_end)

    def get_color(self) -> str:
        if isinstance(self.color, str):
            return self.color
        start = self.color[0].lstrip('#')[0:2]
        end = self.color[1].lstrip('#')[0:2]
        rand_int_value = random.randint(int(start, 16), int(end, 16))
        hex_string = hex(rand_int_value)[2:]
        if len(hex_string) == 1:
            hex_string = f'0{hex_string}'
        return f'#{hex_string * 3}'

    def next(self):
        if self.generated_count == self.count:
            raise StopIteration
        self.generated_count += 1

        shearing_interval = (0, self.shearing_angle) if isinstance(self.shearing_angle, int) else self.shearing_angle

        space_width = self.get_space_width()
        character_spacing = self.get_int_in_interval(self.character_spacing)
        color = self.get_color()

        return (
            FakeTextDataGenerator.generate(
                self.generated_count,
                self.strings[(self.generated_count - 1) % len(self.strings)],
                self.fonts[(self.generated_count - 1) % len(self.fonts)],
                None,
                self.size,
                None,
                self.skewing_angle,
                False,  # random_skew
                self.blur,
                self.random_blur,
                self.background_type,
                self.distorsion_type,
                self.distorsion_orientation,
                self.is_handwritten,
                0,
                self.width,
                self.alignment,
                color,  # text_color
                self.orientation,
                space_width,
                character_spacing,
                self.margins,
                self.fit,
                self.output_mask,
                self.word_split,
                self.image_dir,
                self.stroke_width,
                color,  # stroke_fill
                self.image_mode,
                self.output_bboxes,
                shearing_interval=shearing_interval,
                word_pos_variance=self.word_pos_variance,
            ),
            self.strings[(self.generated_count - 1) % len(self.strings)],
        )
