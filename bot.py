import datetime
import os
from dotenv import load_dotenv
import re
import asyncio
from telegram import ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler
from keep_alive import keep_alive


load_dotenv()
token=os.getenv('MAJLIS_TOKEN')

# Dictionnaire pour compter le nombre de questions posées chaque jour


# Activer les logs pour voir les erreurs
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# 📌 Lire le token depuis le fichier apikey



TOKEN = token
questions_today = {}

last_question_number = {}
user_welcome_messages = {}


# Fonction /start
async def start(update: Update, context: CallbackContext) -> None:
    if update.message:
        chat_type = update.message.chat.type
        if chat_type == "private":
            await update.message.reply_text("👋 Salut ! Je suis actif en mode privé.")
        else:
            await update.message.reply_text("✅ Je suis actif dans ce groupe !")


# ✅ Fonction pour obtenir un `@username` même si l'utilisateur n'en a pas



def get_mention(user):
    """Retourne `@username` si disponible, sinon mentionne via `tg://user?id=USER_ID`."""
    if user.username:
        return f"@{user.username}"  # ✅ Mention normale avec username
    else:
        # Nettoyer le prénom pour éviter les erreurs MarkdownV2
        first_name = user.first_name if user.first_name else "Utilisateur"
        clean_name = re.sub(r"([_*[\]()~`>#+-=|{}.!])", r"\\\1", first_name)

        # ✅ Mention avec ID utilisateur (fonctionne même sans username)
        return f"[{clean_name}](tg://user?id={user.id})"


# ✅ Fonction pour accueillir les nouveaux membres avec @username ou @NomPrenom

# Activer les logs pour voir les erreurs
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Stockage des messages de bienvenue envoyés

# ✅ Fonction pour accueillir les nouveaux membres et gérer l'acceptation


# Activer les logs
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

async def welcome_new_member(update: Update, context: CallbackContext) -> None:
    """Gère l'arrivée des nouveaux membres et affiche un bouton 'Accepter'."""
    if update.message and update.message.new_chat_members:
        for new_member in update.message.new_chat_members:
            try:
                mention = get_mention(new_member)

                # ✅ Créer le bouton "Accepter"
                keyboard = [[InlineKeyboardButton("✅ Accepter", callback_data=f"accept_{new_member.id}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)

                # ✅ Message de bienvenue avec bouton
                rules_message = f"""
🎉 *Bienvenue {mention} dans le groupe* *Q\\&R Malikiyyah* \\! 🎊

📌 *__Comment poser une question__ \\?*
\\#N° \\[suivre l'ordre\\] \\+ N° \\[suivre l'ordre du jour\\] \\+ Question  
Exemple : \\#625 1 L'urine de bébé est\\-elle impure \\?

📌 *__OBJECTIF DU GROUPE__* :
Trouver des réponses à vos questions de fiqh, de 'aqiidah et de tasawwuf touchant à votre pratique\\.

⚠️ Ce groupe *n’est pas un substitut* à l’apprentissage de votre religion\\.
📌 **[Pour suivre des cours cliquez ici](https://www.notion.so/majlisalfatih/Cours-574a6ea54b2d4134b18a7d362ca7d00f)**

📌 *__Qui répond aux questions ici__ \\?*
• **Abdullah Mathieu Gallant**
• **Saifoullah Abu Muhammad**
• **Admin\\(s\\) \\( @ibtisaamou pour les sœurs \\)**

📌 **[Pour connaître leur cursus, leurs shuyuukh, clique ici](https://www.notion.so/majlisalfatih/46691c76bd6e441483fcdd211d5880df\\?v\\=ec736494d7cd446783c655cb0dbb6e58)**

Ils sont tous deux des étudiants avancés en sciences islamiques qui ont l'autorisation de leurs shuyûkh pour enseigner et répondre aux questions, mais ils ne pourront pas avoir réponse à tout\\.

S'ils ne connaissent pas la réponse, vous serez redirigés vers un mufti francophone\\.

📌 **Lien d'invitation Q&R Malikiyyah: https://t.me/+ZBL9frEFpvYyNThh**

📌 *__RÈGLES DU GROUPE__*  

• ⚠️ *Une seule question par membre par jour* ⚠️  
• ⚠️ *__NUMÉROTEZ VOS QUESTIONS SVP__* ⚠️  
• Les enseignants ont besoin de faire des recherches pour certaines questions, aussi par respect nous vous demandons de ne pas les relancer systématiquement mais de patienter 24h avant de le faire\\.  
• Pas de questions théoriques sans application pratique \\(ex\\. hukm de manger de la sirène\\)\\.  
• Vous pouvez demander des précisions si la réponse donnée n'est pas claire, mais évitez de demander le raison d'être et les preuves des statuts juridiques\\.  
• **__Interdit de partager les réponses sans permission__**  
• Pas de débats ni d’échanges entre les membres\\.  
• Il n'est pas permis de répondre à la place des admins\\.  

⚠️ *__Non respect \\= EXPULSION__*  

📌 *__À TITRE INFORMATIF__*  

**Veuillez vous adresser à l'IFI https://institut-francophone-iftaa.com/question** si vous avez besoin d'une fatwa\\.  
• Nous déclinons toute responsabilité si les gens comprennent mal cela et mettent ces réponses en pratique au lieu de s’adresser à un mufti\\.  
• *Pas de réponse aux questions sensibles, contactez* @questionsprivees  

📌 **✅ {mention}, pour continuer, veuillez cliquer sur "accepter"\\.**  
"""


                # ✅ Envoyer le message avec le bouton "Accepter"
                message = await update.message.reply_text(rules_message, parse_mode="MarkdownV2", reply_markup=reply_markup)

                # 🔹 Sauvegarder l'ID du message pour suppression plus tard
                context.chat_data[new_member.id] = message.message_id

            except Exception as e:
                logging.error(f"Erreur lors de l'envoi du message de bienvenue : {e}")

async def button_click(update: Update, context: CallbackContext) -> None:
    """Gère l'événement lorsque l'utilisateur clique sur 'Accepter'."""
    query = update.callback_query
    user_id = int(query.data.split("_")[1])  # Extraire l'ID de l'utilisateur depuis le callback_data
    chat_id = query.message.chat_id

    if query.from_user.id != user_id:
        await query.answer("❌ Vous ne pouvez pas accepter les règles pour quelqu'un d'autre.", show_alert=True)
        return

    try:
        # ✅ Supprimer le message de bienvenue
        welcome_message_id = context.chat_data.get(user_id)
        if welcome_message_id:
            await context.bot.delete_message(chat_id, welcome_message_id)
            del context.chat_data[user_id]  # Nettoyer la variable

        # ✅ Supprimer le message du bouton "Accepter"
        #await query.message.delete()

        # ✅ Envoyer un message de confirmation
        await query.message.reply_text(
            f"✅ Merci {query.from_user.first_name}, vous avez accepté les règles du groupe !",
            parse_mode="MarkdownV2"
        )

    except Exception as e:
        logging.error(f"Erreur lors de la suppression des messages : {e}")



async def check_acceptance(update: Update, context: CallbackContext) -> None:
    """Gère la validation des règles et supprime le message après acceptation."""

    if update.message and update.message.text.strip().lower() == "accepter":
        user_id = update.message.from_user.id
        chat_id = update.message.chat_id

        # Récupérer l'ID du message de bienvenue
        welcome_message_id = context.chat_data.get(user_id)

        try:
            # ✅ Supprimer le message "accepter"
            await update.message.delete()
        except Exception as e:
            logging.error(f"Impossible de supprimer le message 'accepter' : {e}")

        if welcome_message_id:
            try:
                # ✅ Supprimer le message de bienvenue
                await context.bot.delete_message(chat_id, welcome_message_id)
                del context.chat_data[user_id]  # Nettoyer le stockage
            except Exception as e:
                logging.error(f"Impossible de supprimer le message de bienvenue : {e}")

        # ✅ Envoyer une confirmation
        mention = update.message.from_user.first_name
        await update.message.reply_text(
            f"✅ Merci {mention}, vous avez accepté les règles du groupe !",
            parse_mode="MarkdownV2"
        )


# Fonction pour vérifier si un message respecte le bon format de numérotation
async def check_question_number(update: Update, context: CallbackContext) -> None:
    """Vérifie si un message est bien numéroté et suit l'ordre des questions."""
    if update.message:
        user = update.message.from_user
        message_text = update.message.text.strip()  # Supprimer les espaces inutiles
        chat_id = update.message.chat_id
        mention = get_mention(user)  # ✅ Utilisation de get_mention()

        # ✅ Ignorer les messages contenant "accepter" (toutes variations de casse)
        if message_text.lower() == "accepter":
            return

        # ✅ Vérifier que ce n'est pas une réponse à un autre message
        if update.message.reply_to_message is None:
            # ✅ Vérifier si l'utilisateur est un admin
            chat_member = await context.bot.get_chat_member(chat_id, user.id)
            if chat_member.status in ["administrator", "creator"]:
                return  # Les admins ne sont pas concernés

            # ✅ Vérifier si le message commence par #
            match = re.match(r"#(\d+)", message_text)
            if not match:
                await update.message.reply_text(f"{mention} Veuillez numéroter votre question s'il vous plaît.")
                return

            question_number = int(match.group(1))  # Extraire le numéro après #

            # ✅ Vérifier si le numéro suit bien l'ordre croissant
            if chat_id in last_question_number:
                expected_number = last_question_number[chat_id] + 1
                if question_number != expected_number:
                    await update.message.reply_text(
                        f"{mention} Veuillez numéroter votre question avec le #{expected_number} s'il vous plaît."
                    )
                    return
            else:
                expected_number = 1  # Premier message dans le groupe

            # ✅ Mettre à jour le dernier numéro utilisé dans ce groupe
            last_question_number[chat_id] = question_number

    await check_and_close_group(update, context)  # Vérifier si la limite de 10 questions est atteinte


# ✅ Fonction pour supprimer un message hors sujet avec /hs (réservé aux admins)
async def remove_off_topic(update: Update, context: CallbackContext) -> None:
    """Supprime un message hors sujet et aussi le message /hs de l'admin."""
    if update.message and update.message.reply_to_message:
        admin_user = update.message.from_user
        chat_id = update.message.chat_id
        message_to_delete = update.message.reply_to_message
        target_user = message_to_delete.from_user  # L'utilisateur dont le message est supprimé

        # Vérifier si l'utilisateur qui exécute /hs est un admin
        chat_member = await context.bot.get_chat_member(chat_id, admin_user.id)
        if chat_member.status not in ["administrator", "creator"]:
            await update.message.reply_text("❌ Seuls les admins peuvent utiliser cette commande.")
            return

        try:
            # ✅ Supprimer le message hors sujet
            await context.bot.delete_message(chat_id, message_to_delete.message_id)



            # ✅ Mentionner l'utilisateur concerné
            mention = f"@{target_user.username}" if target_user.username else f"[{target_user.first_name}](tg://user?id={target_user.id})"

            # ✅ Envoyer un message expliquant la suppression
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ {mention}, *votre message a été supprimé car il est hors sujet.*\n\n"
                     "📌 **Seules les questions liées à la croyance, au fiqh malikite et à la spiritualité qui touchent votre quotidien sont autorisées.**\n"
                     "Merci de respecter les règles du groupe.",
                parse_mode="Markdown"

            )

            # ✅ Supprimer aussi le message de l'admin contenant /hs
            await context.bot.delete_message(chat_id, update.message.message_id)

        except Exception as e:
            logging.error(f"Erreur lors de la suppression du message hors sujet : {e}")
            await update.message.reply_text("❌ Impossible de supprimer ce message.")


# ✅ Fonction pour expulser un utilisateur avec /wawas (réservé aux admins)
async def remove_waswas_message(update: Update, context: CallbackContext) -> None:
    """Supprime un message si un admin utilise /wawas en réponse et informe l'utilisateur directement dans le groupe."""
    if update.message and update.message.reply_to_message:
        admin = update.message.from_user
        chat_id = update.message.chat_id
        message_to_delete = update.message.reply_to_message
        target_user = message_to_delete.from_user  # Utilisateur dont le message est supprimé

        # Vérifier si l'utilisateur est un admin
        chat_member = await context.bot.get_chat_member(chat_id, admin.id)
        if chat_member.status not in ["administrator", "creator"]:
            await update.message.reply_text("❌ Seuls les admins peuvent utiliser cette commande.")
            return

        try:
            # ✅ Supprimer le message du membre contenant du waswas
            await context.bot.delete_message(chat_id, message_to_delete.message_id)

            # ✅ Mentionner l'utilisateur concerné
            mention = f"@{target_user.username}" if target_user.username else f"[{target_user.first_name}](tg://user?id={target_user.id})"

            # ✅ Envoyer un message expliquant la suppression
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ {mention}, *votre message a été supprimé, car il pourrait causer des wasâwis aux autres membres* \n\n"
                     f"(doutes maladifs nuisant à la pratique religieuse).\n\n"
                     "📌 *Veuillez poser votre question en privé à  @questionsprivees.*\n"
                     "Merci de votre compréhension.",
                parse_mode="Markdown"
            )

            # ✅ Supprimer le message de l'admin contenant /wawas
            await context.bot.delete_message(chat_id, update.message.message_id)


        except Exception as e:
            logging.error(f"Erreur lors de la suppression du message de waswas : {e}")
            await update.message.reply_text("❌ Impossible de supprimer ce message.")


async def check_and_close_group(update: Update, context: CallbackContext) -> None:
    """Ferme le groupe si 10 questions ont été posées dans la journée."""
    global questions_today

    if update.message:
        chat_id = update.message.chat_id
        today = datetime.date.today()

        # Vérifier si c'est une nouvelle journée (reset du compteur)
        if chat_id not in questions_today or questions_today[chat_id]["date"] != today:
            questions_today[chat_id] = {"count": 0, "date": today}

        # Extraire le numéro de la question
        message_text = update.message.text
        match = re.match(r"#(\d+)", message_text)

        if match:
            questions_today[chat_id]["count"] += 1
            print(f"📊 Nombre de questions posées aujourd'hui : {questions_today[chat_id]['count']}")

            # Si 10 questions ont été posées, on ferme le groupe
            if questions_today[chat_id]["count"] >= 10:
                await close_group_until_midnight(update, context)


async def close_group_until_midnight(update: Update, context: CallbackContext) -> None:
    """Ferme le groupe jusqu'à minuit."""
    chat_id = update.message.chat_id

    try:
        # 🔒 Bloquer l'envoi de messages
        await context.bot.set_chat_permissions(
            chat_id=chat_id,
            permissions=ChatPermissions(
                can_send_messages=False  # Désactiver les messages
            )
        )

        # 📢 Envoyer un message d'information
        await update.message.reply_text(
            "⚠️ *La limite de 10 questions a été atteinte pour aujourd’hui.*\n\n"
            "📌 *Le groupe est fermé jusqu'à minuit.*\n"
            "📌 *En cas d’urgence, contactez @questionsprivees.*",
            parse_mode="Markdown"
        )

        # ⏳ Calcul du temps restant jusqu'à minuit
        now = datetime.datetime.now()
        midnight = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0, 0))
        seconds_until_midnight = (midnight - now).total_seconds()

        # ✅ Planifier la réouverture du groupe à minuit
        asyncio.create_task(reopen_group_at_midnight(chat_id, context, seconds_until_midnight))

    except Exception as e:
        logging.error(f"Erreur lors de la fermeture du groupe : {e}")


async def reopen_group_at_midnight(chat_id, context, delay):
    """Attend jusqu'à minuit et réactive les messages."""
    await asyncio.sleep(delay)  # Attendre jusqu'à 00h00

    try:
        # 🔓 Réactiver les messages
        await context.bot.set_chat_permissions(
            chat_id=chat_id,
            permissions=ChatPermissions(
                can_send_messages=True  # Permettre à nouveau les messages
            )
        )

        # 📢 Envoyer un message de réouverture
        await context.bot.send_message(
            chat_id=chat_id,
            text="✅ *Les questions sont à nouveau ouvertes !* Vous pouvez poser vos questions.",
            parse_mode="Markdown"
        )

        # 🎯 Réinitialiser le compteur pour la nouvelle journée
        questions_today[chat_id] = {"count": 0, "date": datetime.date.today()}

    except Exception as e:
        logging.error(f"Erreur lors de la réouverture du groupe : {e}")


# ✅ Fonction principale
def main():

    keep_alive()  # Garde le bot en ligne

    logging.info("Démarrage du bot...")

    app = Application.builder().token(TOKEN).build()

    #
    app.add_handler(CommandHandler("start", start))

    # Gestion des nouveaux membres
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

    # Vérification du format et de l'ordre des questions
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_question_number))

    # Vérification de l'acceptation des règles
    #app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_acceptance))

    # fonction hs
    app.add_handler(CommandHandler("hs", remove_off_topic))

    # wawas
    app.add_handler(CommandHandler("waswas", remove_waswas_message))

    # app.add_handler(CommandHandler("10", close_group_for_6h))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_and_close_group))

    #boutton
    app.add_handler(CallbackQueryHandler(button_click, pattern=r"^accept_\d+$"))

    # Lancer le bot
    app.run_polling()


if __name__ == "__main__":
    main()
