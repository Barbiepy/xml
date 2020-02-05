from datetime import datetime
from lxml import etree
import sys


class ProcessXmlException(Exception):
    """Кастомный exception"""
    pass


def write_log_message(message: str) -> None:
    """
    Функция записи сообщений в лог
    :param message:
    :return:
    """
    with open("logs.txt", 'a') as f:
        f.write(f"{datetime.now().isoformat(timespec='minutes')} {message}\n")


def process_xml(input_xml_name: str,
                input_schema_name: str,
                xslt_name: str,
                result_schema_name: str,
                result_xml_name: str) -> None:
    """
    Проверка xml файла по xsd схеме, xslt трансформация, проверка сформированного xml по xsd схеме и запись
    в файл если все прошло успешно

    :param input_xml_name: имя обрабатываемого xml файла
    :param input_schema_name: имя схемы для первичной проверки xml файла
    :param xslt_name:  имя файла по которому нужно провести трансформацию
    :param result_schema_name: имя схемы для проверки полученного в результате трансформации файла
    :param result_xml_name: имя для полученного в результате трансформации xml файла
    :return: None
    """

    try:
        input_schema_root = etree.parse(input_schema_name)
        input_tree = etree.parse(input_xml_name)
        xslt_root = etree.parse(xslt_name)
        result_schema_root = etree.parse(result_schema_name)

    except Exception as e:
        write_log_message(f"Не удалось открыть файл: {e}")
        raise ProcessXmlException("Ошибка при обработке xml, логи в файле logs.txt")

    input_schema = etree.XMLSchema(input_schema_root)

    try:
        input_schema.assertValid(input_tree)
        write_log_message(f"Валидация входящего файла {input_xml_name} по схеме {input_schema_name} прошла успешно")
    except Exception as e:
        write_log_message(f"Ошибка при валидации входящего файла {input_xml_name} по схеме {input_schema_name} : {e}")
        raise ProcessXmlException("Ошибка при обработке xml, логи в файле logs.txt")

    transform = etree.XSLT(xslt_root)

    try:
        result_tree = transform(input_tree)
        write_log_message(f"Трансформация файла {input_xml_name} по таблице {result_schema_name} прошла успешно")

    except Exception as e:
        write_log_message(f"Ошибка при трансформации xml {input_xml_name} по таблице {result_schema_name} : {e}")
        raise ProcessXmlException("Ошибка при обработке xml, логи в файле logs.txt")

    result_schema = etree.XMLSchema(result_schema_root)

    try:
        result_schema.assertValid(result_tree)
        write_log_message(f"Валидация трансформированного файла по схеме {result_schema_name} прошла успешно")
    except Exception as e:
        write_log_message(f"Ошибка при валидации трансформированного файла по схеме {result_schema_name}: {e}")
        raise ProcessXmlException("Ошибка при обработке xml, логи в файле logs.txt")

    result_string = etree.tostring(result_tree, pretty_print=True, encoding='unicode')

    with open(result_xml_name, 'w') as f:
        f.write(result_string)


if __name__ == '__main__':
    input_xml_name = sys.argv[1]
    input_schema_name = sys.argv[2]
    xslt_name = sys.argv[3]
    result_schema_name = sys.argv[4]
    result_xml_name = sys.argv[5]

    process_xml(input_xml_name, input_schema_name, xslt_name, result_schema_name, result_xml_name)
    print(f"Сформирован файл {result_xml_name}")
