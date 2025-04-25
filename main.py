# Importações necessárias para o funcionamento do bot
# #from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, Updater, CallbackQueryHandler
#from ntscraper import Nitter
#import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
#from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from chaves import BEARER_TOKEN, BOT_USERNAME,TOKEN

# ======================== Comandos do Bot =========================== #

# /start – Mensagem de boas-vindas com os comandos disponíveis
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem = (
        "🎮 Bem-vindo ao Bot da FURIA! 🐯\n"
        "O seu canal direto com tudo sobre o time de CS da FURIA!\n\n"
        "💥 Comandos disponíveis:\n"
        "/jogos – Veja os próximos confrontos da FURIA\n"
        "/time – Conheça o elenco atual\n"
        "/curiosidade – Descubra fatos legais sobre o time\n"
        "/noticias – Receba as últimas novidades\n"
        "/redes – Acompanhe a FURIA nas redes sociais\n"
        "📣 Atualizações rápidas, curiosidades, e aquele clima de torcida raiz!"
    )
    if update.message:
        await update.message.reply_text(mensagem)
    elif update.callback_query:
        await update.callback_query.edit_message_text(mensagem)

# /help – Explica o propósito do bot
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Eu sou um chatbot feito para te manter informado sobre o time de CS da FURIA!\n"
        "Para me usar veja a lista de comandos e digite ou clique em algum!!"
    )

# /jogos – Lista de próximos jogos
async def jogos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📅 Os próximos confrontos da FURIA são:\n"
                                    "- FURIA vs Team Liquid - 27/04 às 18h\n"
                                    "- FURIA vs NAVI - 30/04 às 20h\n"
                                    "- FURIA vs Imperial - 02/05 às 17h")

# /time – Mostra o elenco atual com imagem
async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo="https://i.imgur.com/iFLlTVg.jpeg",
        caption="👥 Elenco atual da FURIA CS:GO:\n"
                "- FalleN 🇧🇷\n"
                "- KSCERATO 🇧🇷\n"
                "- yuurih 🇧🇷\n"
                "- YEKINDAR 🇱🇻\n"
                "- molodoy 🇰🇿\n"
    )

# /curiosidade – Envia curiosidades sobre a FURIA
async def curiosidade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 Curiosidades sobre a FURIA:\n"
                                    "- A FURIA foi fundada em 2017.\n"
                                    "- É uma das primeiras organizações brasileiras com foco em performance e estilo de jogo agressivo.\n"
                                    "- A FURIA já representou o Brasil em diversos Majors de CS:GO!")

# /noticias – Envia uma notícia com botões inline para navegar
async def noticias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Próxima notícia", callback_data="next_news")],
        [InlineKeyboardButton("Voltar ao menu", callback_data="menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("📰 Últimas novidades da FURIA:\n"
                                    "- FURIA anuncia novo patrocinador!",
                                    reply_markup=reply_markup,
                                    parse_mode="Markdown")

# Lida com os botões inline clicados pelo usuário
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "next_news":
        await query.edit_message_text(
            text="📰 *Notícia 2:*\n- Mudanças estratégicas para o próximo campeonato.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Próxima", callback_data="next_news_2")],
                [InlineKeyboardButton("Voltar ao menu", callback_data="menu")],
            ])
        )
    elif query.data == "next_news_2":
        await query.edit_message_text(
            text="📰 *Notícia 3:*\n- FalleN comenta planos para o segundo semestre.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Voltar ao menu", callback_data="menu")]
            ])
        )
    elif query.data == "menu":
        await start(update, context)

# /redes – Links para redes sociais
async def redes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌐 Redes sociais da FURIA:\n"
                                    "- Twitter: https://twitter.com/furiagg\n"
                                    "- Instagram: https://instagram.com/furiagg")

# ======================== Integração com Twitter =========================== #

# Busca tweets com Nitter (caso queira testar sem API oficial) - função usada para aprendizado
def buscar_tweets_furia():
    from ntscraper import Nitter
    print("Buscando tweets furia")
    scraper = Nitter(log_level=2, skip_instance_check=True)
    scraper.set_instance("nitter.poast.org")

    try:
        tweets = scraper.get_tweets("Furia", mode='user', number=1, timeout=10)
        print("✅ Tweet encontrado:", tweets)
        return tweets
    except Exception as e:
        print("❌ Erro ao buscar tweets:", e)
        return []

# /tweet – Captura o último tweet usando Selenium
async def furia_tweet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tweet = await twitter_search(update, context)
    if tweet:
        await update.message.reply_text(f"🐦 Último tweet da FURIA:\n\n{tweet}")
    else:
        await update.message.reply_text("❌ Não consegui encontrar tweets da FURIA.")

# Função para capturar tweets com Selenium
async def twitter_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    options = Options()
    options.add_argument("--headless")  # Executa o navegador sem abrir janela

    driver = webdriver.Chrome(options=options)
    driver.get("https://x.com/furia")
    noticia = ""

    try:
        tweet_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//article//div[@data-testid='tweetText']"))
        )
        noticia += tweet_element.text
        print("✅ Notícia capturada:", noticia)
    except Exception as e:
        print("❌ Erro ao capturar tweet:", e)
        noticia = ""

    driver.quit()
    return noticia

# ======================== Mensagens genéricas =========================== #

# Respostas automáticas para textos específicos
def handle_response(text: str) -> str:
    processed = text.lower()

    if "im starting to believe it as well henry" in processed:
        return ("Because he's gonna take down another one!\n"
                "Fallen!\n"
                "Stop blowing my mind!\n"
                "This is not NA, this is a Major!\n"
                "James is gonna be picking up the kill...\n"
                "Fallen, another one!\n"
                "Oh my God, he's doing it!\n"
                "Fallen is in the house baby!\n"
                "And Liquid... they are falling apart!")

    if "oi" in processed:
        return "Oi FURIOSO/A"

    return "Eu não entendi o que você escreveu"

# Lida com mensagens de texto enviadas por usuários
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == "group":
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, "").strip()
            response = handle_response(new_text)
        else:
            return
    else:
        response = handle_response(text)

    print("Bot:", response)
    await update.message.reply_text(response)

# ======================== Inicialização =========================== #

# Lida com erros da aplicação
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

# Execução principal do bot
if __name__ == '__main__':
    print("Starting Telegram Bot...")
    app = Application.builder().token(TOKEN).build()

    # Handlers de comando
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("jogos", jogos))
    app.add_handler(CommandHandler("time", time))
    app.add_handler(CommandHandler("curiosidade", curiosidade))
    app.add_handler(CommandHandler("noticias", noticias))
    app.add_handler(CommandHandler("redes", redes))
    app.add_handler(CommandHandler("tweet", furia_tweet))

    # Handler para botões inline (notícias)
    app.add_handler(CallbackQueryHandler(button_handler))

    # Handler para mensagens genéricas
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Handler de erros
    app.add_error_handler(error)

    # Inicia o bot
    print("Lendo...")
    app.run_polling()