# signal-flags-emoji

[![License: CC0-1.0](https://img.shields.io/badge/License-CC0--1.0-lightgrey.svg)](LICENSE)

26 морских сигнальных флагов из предоставленного архива и добавленных исходников, обработанные для использования рядом с текстом в Telegram. Готовые файлы — **PNG RGBA, 100 × 100 px, sRGB**, с прозрачным фоном, исходными цветами и тенями. Полотнище занимает до 90 × 90 px, пропорции сохранены.

**[Добавить эмодзи в Telegram — HoistTheFlags](https://t.me/addemoji/HoistTheFlags)**

<p>
  <img src="emoji/a-alfa.png" width="32" height="32" alt="A Alfa" title="A Alfa">
  <img src="emoji/b-bravo.png" width="32" height="32" alt="B Bravo" title="B Bravo">
  <img src="emoji/c-charlie.png" width="32" height="32" alt="C Charlie" title="C Charlie">
  <img src="emoji/d-delta.png" width="32" height="32" alt="D Delta" title="D Delta">
  <img src="emoji/e-echo.png" width="32" height="32" alt="E Echo" title="E Echo">
  <img src="emoji/f-foxtrot.png" width="32" height="32" alt="F Foxtrot" title="F Foxtrot">
  <img src="emoji/g-golf.png" width="32" height="32" alt="G Golf" title="G Golf">
  <img src="emoji/h-hotel.png" width="32" height="32" alt="H Hotel" title="H Hotel">
  <img src="emoji/i-india.png" width="32" height="32" alt="I India" title="I India">
  <img src="emoji/j-juliett.png" width="32" height="32" alt="J Juliett" title="J Juliett">
  <img src="emoji/k-kilo.png" width="32" height="32" alt="K Kilo" title="K Kilo">
  <img src="emoji/l-lima.png" width="32" height="32" alt="L Lima" title="L Lima">
  <img src="emoji/m-mike.png" width="32" height="32" alt="M Mike" title="M Mike">
  <img src="emoji/n-november.png" width="32" height="32" alt="N November" title="N November">
  <img src="emoji/o-oscar.png" width="32" height="32" alt="O Oscar (вариант)" title="O Oscar (вариант)">
  <img src="emoji/p-papa.png" width="32" height="32" alt="P Papa" title="P Papa">
  <img src="emoji/q-quebec.png" width="32" height="32" alt="Q Quebec" title="Q Quebec">
  <img src="emoji/r-romeo.png" width="32" height="32" alt="R Romeo" title="R Romeo">
  <img src="emoji/s-sierra.png" width="32" height="32" alt="S Sierra" title="S Sierra">
  <img src="emoji/t-tango.png" width="32" height="32" alt="T Tango" title="T Tango">
  <img src="emoji/u-uniform.png" width="32" height="32" alt="U Uniform" title="U Uniform">
  <img src="emoji/v-victor.png" width="32" height="32" alt="V Victor" title="V Victor">
  <img src="emoji/w-whiskey.png" width="32" height="32" alt="W Whiskey" title="W Whiskey">
  <img src="emoji/x-x-ray.png" width="32" height="32" alt="X X-ray (вариант)" title="X X-ray (вариант)">
  <img src="emoji/y-yankee.png" width="32" height="32" alt="Y Yankee (вариант)" title="Y Yankee (вариант)">
  <img src="emoji/z-zulu.png" width="32" height="32" alt="Z Zulu" title="Z Zulu">
</p>

## Готовые файлы и просмотр

- [emoji/](emoji/) — PNG для загрузки в Telegram **файлами**, без сжатия фотографий.
- [processed/](processed/) — обработанные изображения 1024 × 1024 или 2048 × 2048 px с прозрачностью.
- [Контактный лист на белом](previews/contact-white.png) и [на тёмном](previews/contact-dark.png) — каждый флаг в 20, 24, 32 и 100 px и рядом с текстом при 24 px. Открывайте оригинал изображения в масштабе 100%, чтобы оценить реальные размеры.
- [Сравнения до/после](previews/) — `comparison-01.png` … `comparison-05.png`.
- [Каталог](CATALOG.md), [CSV](catalog.csv), [инструкция Telegram](docs/telegram.md), [отчёт проверки](docs/quality.md).

В наборе все 26 букв A–Z. Обозначения определены по рисунку; 23 изображения определены уверенно; O Oscar (переставлены цвета), X X-ray (добавлен диагональный крест) и Y Yankee (пересекающая полоса) — предположительные варианты, отмеченные знаком `?` на превью и в каталоге. Точная идентификация X не подтверждена. Это обработка предоставленной декоративной графики, а не исправленный нормативный справочник морских сигналов.

## Структура

```text
originals/       исходные байты, имена по буквам
processed/       PNG RGBA в исходном разрешении
emoji/           PNG RGBA 100 × 100
previews/        контактные листы и сравнения
scripts/         обработка, экспорт, настройки каждого флага
scripts/flags.json  каталог исходников, SHA-256, палитра и overrides
docs/            инструкция, описание обработки, результаты проверок
```

Все исходники переименованы по буквам: `a-alfa.jpg`, `b-bravo.jpg` и т. д. Содержимое файлов не изменено. У 22 архивных файлов ранее было ошибочное расширение `.png`, хотя фактический формат — **JPEG RGB**. Расширение `.jpg` теперь соответствует содержимому. Прежние имена сохранены в `catalog.csv` и `scripts/flags.json`; настоящие PNG создаются только в выходных папках. Архив, виртуальное окружение, кеши и временные файлы исключены из Git.

## Повторная сборка одной командой

Нужны Python 3.12+ с `venv`, Bash и доступ к PyPI при первой установке зависимостей. Проверено на Python 3.15 / macOS arm64; версии зависимостей закреплены в `requirements.txt`.

```bash
./scripts/build.sh
```

Команда создаёт `.venv`, устанавливает зависимости, проверяет исходные SHA-256, обрабатывает все изображения, создаёт превью и каталог, затем выполняет проверки экспорта. Исходники уже включены в репозиторий, архив для сборки не нужен. Архивные исходники можно восстановить из `Maritime_Signal_Flags.zip` в корне проекта: поле `archive_member` связывает прежнее имя в ZIP с новым именем. Добавленные отдельно файлы нужно восстановить из репозитория или собственной копии.

В [scripts/flags.json](scripts/flags.json) хранятся каталог исходников, SHA-256 и порог выделения внешнего фона (`background_threshold`). Сборка сохраняет исходные цвета, тени, фактуру и обводку. При добавлении исходника добавьте запись с обозначением и SHA-256; неизвестный исходник требует явной записи и статуса идентификации.

Метод и ограничения описаны в [docs/processing.md](docs/processing.md). При обработке нейросетевая генерация и новая отрисовка не применяются.

## Лицензия

Весь проект — исходные изображения, обработанные изображения, эмодзи, превью, скрипты, каталоги и документация — опубликован под **CC0 1.0 Universal (CC0-1.0)**.

Полный официальный текст: [LICENSE](LICENSE). [CC0 на сайте Creative Commons](https://creativecommons.org/publicdomain/zero/1.0/).

## Справочник

Для сверки обозначений использован [справочник флагов ВМС Сингапура](https://www.navy.gov.sg/publications-stories/naval-traditions/naval-flags-and-pennants/).
