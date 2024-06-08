from .maps import get_sorted_list_and_legs, generate_static_map
from fpdf import FPDF, Align
import string
import os

class PDF(FPDF):
    """
    Klasa PDF do generowania plików PDF z planem zwiedzania.

    :param image_url: URL obrazu mapy
    :param plan_table: Tabela z planem zwiedzania
    :param summary_table: Tabela z podsumowaniem
    """
    def __init__(self, image_url, plan_table, summary_table):
        super().__init__()
        self.add_page()
        self.path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static/fonts'))
        self.add_font("dejavu-sans", style="", fname=os.path.join(self.path, 'DejaVuSans.ttf'))
        self.add_font("dejavu-sans", style="b", fname=os.path.join(self.path, 'DejaVuSans-Bold.ttf'))
        self.add_font("dejavu-sans", style="i", fname=os.path.join(self.path, 'DejaVuSans-Oblique.ttf'))
        self.add_font("dejavu-sans", style="bi", fname=os.path.join(self.path, 'DejaVuSans-BoldOblique.ttf'))
        self.set_font("dejavu-sans")

        self.add_title("Plan zwiedzania")
        self.add_image(image_url)
        self.add_plan_table(plan_table)
        self.add_summary_table(summary_table)

    def add_title(self, title):
        """
        Dodaje tytuł do dokumentu PDF.

        :param title: Tytuł dokumentu
        """
        self.set_x(22)
        self.set_y(20)
        self.set_font_size(14)
        self.text(x=self.get_x()+12, y=self.get_y(), txt=title)

    def add_image(self, url):
        """
        Dodaje obraz do dokumentu PDF.

        :param url: URL obrazu
        """
        self.set_y(27)
        self.image(url, x=Align.C, y=self.get_y(), w=165)
        self.set_y(212)

    def add_plan_table(self, plan_table):
        """
        Dodaje tabelę z planem zwiedzania do dokumentu PDF.

        :param plan_table: Tabela z planem zwiedzania
        """
        self.set_font_size(11)

        with self.table(width=175, col_widths=(62.5, 62.5, 25, 25), text_align="CENTER", borders_layout="INTERNAL") as table:
            for data_row in plan_table:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)

        for i in range(4):
            self.ln()

    def add_summary_table(self, summary_table):
        """
        Dodaje tabelę z podsumowaniem do dokumentu PDF.

        :param summary_table: Tabela z podsumowaniem
        """
        self.set_font_size(11)
        self.text(x=self.get_x() + 7, y=self.get_y(), text="Podsumowanie:")
        self.ln()

        with self.table(width=175, col_widths=(20, 110, 20, 25), text_align="CENTER", borders_layout="INTERNAL") as table:
            for data_row in summary_table:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)

        self.ln()
        suma = sum(int(float(row[2])) * int(float(row[3])) for row in summary_table[1:])
        self.text(x=self.get_x() + 145, y=self.get_y(), txt=f"Łączna cena: {suma}")

    def output_pdf(self, filename):
        """
        Zapisuje dokument PDF do pliku.

        :param filename: Nazwa pliku wyjściowego
        """
        self.output(filename)


def generate_pdf(start_loc: str, loc_list: list, quantities: list, mode: str ='walking') -> PDF:
    """
    Generuje plik PDF z planem zwiedzania.

    :param start_loc: Lokalizacja początkowa
    :param loc_list: Lista lokalizacji
    :param quantities: Lista ilości
    :param mode: Tryb podróży (domyślnie 'walking')
    :return: Obiekt PDF
    """
    image_url, _ = generate_static_map(start_loc, loc_list, mode=mode)

    loc_list = sorted(loc_list, key=lambda obj: obj.nazwa_atrakcji)

    sorted_loc_list, legs = get_sorted_list_and_legs(start_loc, loc_list, mode)

    plan_table = [("Miejsce początkowe", "Miejsce końcowe", "Dystans", "Czas")]
    for i, leg in enumerate(legs):
        row = (sorted_loc_list[i-1].nazwa_atrakcji if i>0 else start_loc, sorted_loc_list[i].nazwa_atrakcji, leg['distance']['text'], leg['duration']['text'])
        plan_table.append(row)

    summary_table = [("Nr", "Nazwa Atrakcji", "Ilość", "Cena/szt")]
    for i, item in enumerate(sorted_loc_list):
        row = (string.ascii_uppercase[i], sorted_loc_list[i].nazwa_atrakcji, str(quantities[i]), str(sorted_loc_list[i].cena_podstawowa))
        summary_table.append(row)

    pdf = PDF(image_url=image_url,
              plan_table=plan_table,
              summary_table=summary_table)

    return pdf
