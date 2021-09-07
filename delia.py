#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Primero, se definen algunas funciones de devolución de llamada. Luego, esas funciones
 se pasan a el Despachador y registrados en sus respectivos lugares.
Luego, el bot se inicia y se ejecuta hasta que presionamos Ctrl-C en la línea de comando.

Uso:
Ejemplo de una conversación de usuario de bot usando ConversationHandler.
Enviar / comenzar para iniciar la conversación.
Presione Ctrl-C en la línea de comando o envíe una señal al proceso para detener el
Bot.
"""

import logging
from typing import Dict

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.error import Unauthorized
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    ['Caso', 'Fecha'],
    ['Novedad', 'Algo más...'],
    ['Salir'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Función auxiliar para formatear la información de usuario recopilada."""
    facts = [f'{key} - {value}' for key, value in user_data.items()]
    return "\n".join(facts).join(['\n', '\n'])


def start(update: Update, context: CallbackContext) -> int:
    """Inicie la conversación y solicite información al usuario."""
    update.message.reply_text(
        "¡Hola! Mi nombre es Delia Flores. Te ayudaré a almacenar datos para tí. "
        "¿Por qué no me das mas información?",
        reply_markup=markup,
    )

    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    """Solicite al usuario información sobre la opción predefinida seleccionada."""
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(f'Tu {text.lower()}? ¡Sí, me encantaría saberlo!')

    return TYPING_REPLY


def custom_choice(update: Update, context: CallbackContext) -> int:
    """Pídale al usuario una descripción de una categoría personalizada."""
    update.message.reply_text(
        'De acuerdo, primero envíeme una categoría, por ejemplo, "Lugar del hecho"'
    )

    return TYPING_CHOICE


def received_information(update: Update, context: CallbackContext) -> int:
    """Almacene la información proporcionada por el usuario y solicite la siguiente categoría."""
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text(
        "¡Listo! Para que lo sepas, esto es lo que ya grabe:"
        f"{facts_to_str(user_data)} Puedes contarme más o considerar algo más"
        " , vamos.",
        reply_markup=markup,
    )

    return CHOOSING


def done(update: Update, context: CallbackContext) -> int:
    """Muestre la información recopilada y finalice la conversación."""
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text(
        f"Acumule esta información por ti: {facts_to_str(user_data)}¡Hasta la proxima vez!",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("1910087417:AAFuuxarMHVaGdGJ4kVSlfc9Era5tsZJs9Q")

    # Consiga que el despachador registre a los manejadores
    dispatcher = updater.dispatcher

    # Agregue un controlador de conversación con los estados CHOOSING, TYPING_CHOICE y TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(Caso|Fecha|Novedad)$'), regular_choice
                ),
                MessageHandler(Filters.regex('^Algo más...$'), custom_choice),
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Salir$')), regular_choice
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Salir$')),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Salir$'), done)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Ejecute el bot hasta que presione Ctrl-C o el proceso reciba SIGINT,
    # SIGTERM o SIGABRT. Esto debe usarse la mayor parte del tiempo, ya que
    # start_polling () no bloquea y detendrá el bot con gracia.
    updater.idle()


if __name__ == '__main__':
    main()