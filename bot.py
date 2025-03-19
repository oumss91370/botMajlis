import os
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import re
from dotenv import load_dotenv
import datetime
import asyncio
from telegram import ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler
from keep_alive import keep_alive

load_dotenv()
token = os.getenv('MAJLIS_TOKEN')
CHAT_ID = -1001912372093  # ⚠️ Remplace avec l'ID réel de ton groupe

# Dictionnaire pour compter le nombre de questions posées chaque jour


# Activer les logs pour voir les erreurs
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 📌 Lire le token depuis le fichier apikey


TOKEN = token
questions_today = {}

last_question_number = {}
user_welcome_messages = {}




# ✅ Fonction pour obtenir un `@username` même si l'utilisateur n'en a pas


def get_mention(user):
    """Retourne @username si disponible, sinon affiche juste le prénom/nom sans lien."""
    try:
        if user.username:
            logging.info(f"ℹ️ Utilisateur trouvé avec username : @{user.username}")
            return f"@{user.username}"
        else:
            first_name = user.first_name if user.first_name else "Utilisateur inconnu"
            clean_name = re.sub(r"([_*[\]()~`>#+-=|{}.!])", r"\\\1", first_name)
            logging.info(f"ℹ️ Utilisateur trouvé sans username, utilisant prénom : {clean_name}")
            return f"@{clean_name}"
    except Exception as e:
        logging.error(f"❌ Erreur dans get_mention() : {e}")
        return "@Utilisateur_Inconnu"


# ✅ Fonction pour accueillir les nouveaux membres avec @username ou @NomPrenom

# Stockage des messages de bienvenue envoyés

# ✅ Fonction pour accueillir les nouveaux membres et gérer l'acceptation


# Activer les logs

async def welcome_new_member(update: Update, context: CallbackContext) -> None:
    """Gère l'arrivée des nouveaux membres et affiche un bouton 'Accepter'."""
    if update.message and update.message.new_chat_members:
        logging.info("🟠 Nouveau membre détecté dans le groupe.")

        for new_member in update.message.new_chat_members:
            try:
                mention = get_mention(new_member)
                logging.info(f"✅ Mention du nouveau membre : {mention}")

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

📌 **[Pour connaître leur cursus, leurs shuyuukh, clique ici](https://www.notion.so/majlisalfatih/46691c76bd6e441483fcdd211d5880df?v=ec736494d7cd446783c655cb0dbb6e58)**

Ils sont tous deux des étudiants avancés en sciences islamiques qui ont l'autorisation de leurs shuyûkh pour enseigner et répondre aux questions, mais ils ne pourront pas avoir réponse à tout\\.

S'ils ne connaissent pas la réponse, vous serez redirigés vers un mufti francophone\\.

📌 **[🔗 Rejoindre le groupe Q\\&R Malikiyyah](https://t.me/+ZBL9frEFpvYyNThh)**

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

📌 **Veuillez vous adresser à [l'IFI](https://institut-francophone-iftaa.com/question)** si vous avez besoin d'une fatwa\\.
• *Pas de réponse aux questions sensibles, les envoyez à * @questionsprivees

📌 **✅ {mention}, pour continuer, veuillez cliquer sur "accepter"\\.**
"""

                # ✅ Envoyer le message avec le bouton "Accepter"
                logging.info("📤 Envoi du message de bienvenue...")
                message = await update.message.reply_text(
                    rules_message,
                    parse_mode="MarkdownV2",
                    reply_markup=reply_markup
                )
                logging.info(f"✅ Message de bienvenue envoyé avec succès pour {mention}.")

                # 🔹 Sauvegarder l'ID du message pour suppression plus tard
                context.chat_data[new_member.id] = message.message_id
                logging.info(f"📋 ID du message sauvegardé : {message.message_id}")

            except Exception as e:
                logging.error(f"❌ Erreur lors de l'envoi du message de bienvenue pour {mention} : {e}")


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
        # await query.message.delete()

        # ✅ Envoyer un message de confirmation
        await query.message.reply_text(
            f"✅ Merci {query.from_user.first_name}, vous avez accepté les règles du groupe !",
            parse_mode="MarkdownV2"
        )

    except Exception as e:
        logging.error(f"Erreur lors de la suppression des messages : {e}")


async def already_answered(update: Update, context: CallbackContext) -> None:
    """Répond automatiquement qu'une question a déjà été traitée lorsque /dr est utilisé en réponse."""

    if update.message and update.message.reply_to_message:
        user = update.message.from_user
        chat_id = update.message.chat_id
        message_to_reply = update.message.reply_to_message

        # ✅ Vérifier si l'utilisateur est un "member" (autoriser tous les autres statuts)
        try:
            chat_member = await context.bot.get_chat_member(chat_id, user.id)

            if chat_member.status == "member":
                await update.message.reply_text("❌ Seuls les admins peuvent utiliser cette commande.")
                return  # ❌ Bloquer uniquement les "members"

        except Exception as e:
            logging.error(f"❌ Erreur lors de la vérification du statut pour {user.id} : {e}")

        try:
            # ✅ Obtenir la mention de l'utilisateur
            mention = get_mention(message_to_reply.from_user)

            # ✅ Envoyer la réponse automatique
            await context.bot.send_message(
                chat_id=chat_id,
                reply_to_message_id=message_to_reply.message_id,
                text=f"⚠️ {mention}, votre question a déjà été traitée.\n\n"
                     "🔍 *Merci de bien vouloir chercher les mots-clés dans la fonction* **'Recherche'**.\n"
                     " Baraakallah u fik !",
                parse_mode="Markdown"
            )

            # ✅ Supprimer la commande /dr après envoi du message
            await update.message.delete()

        except Exception as e:
            logging.error(f"❌ Erreur lors de l'envoi du message /dr : {e}")
            await update.message.reply_text("❌ Impossible d'envoyer le message.")


# ✅ Ajouter la commande au gestionnaire


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


# Dictionnaire pour stocker le dernier message d'un utilisateur
user_last_question_time = {}


async def initialize_last_question_number(context: CallbackContext, chat_id: int):
    """Récupère uniquement le dernier numéro #XXX trouvé dans le groupe et l'utilise comme référence."""
    try:
        last_valid_number = 0  # Valeur par défaut

        updates = await context.bot.get_updates()  # ✅ Récupère les derniers messages reçus par le bot

        for update in reversed(updates):  # 🔹 Parcourt les messages du plus récent au plus ancien
            if update.message and update.message.chat_id == chat_id and update.message.text:
                match = re.search(r"#(\d+)", update.message.text)
                if match:
                    last_valid_number = int(match.group(1))  # ✅ Prend immédiatement le dernier `#` trouvé
                    break  # ✅ Dès qu'on trouve un `#`, on s'arrête

        last_question_number[chat_id] = last_valid_number  # ✅ Mise à jour avec le dernier numéro trouvé
        logging.info(f"✅ Initialisation : dernier numéro trouvé dans {chat_id} → #{last_question_number[chat_id]}")

    except Exception as e:
        logging.error(f"❌ Erreur lors de l'initialisation de last_question_number pour {chat_id} : {e}")
        last_question_number[chat_id] = 0  # Sécurité en cas d'erreur


# ✅ Dictionnaire pour stocker le premier message du user dans le groupe
user_first_message_time = {}
last_reset_date = datetime.date.today()


# ✅ Dictionnaire pour stocker la date de réinitialisation

async def reset_daily_data():
    """Réinitialise les questions quotidiennes et les timestamps tout en conservant les derniers numéros de question."""
    global last_question_number, user_first_message_time, questions_today

    # 🔹 Sauvegarder les dernières valeurs de `last_question_number` uniquement si elle n'est pas vide
    if last_question_number:
        last_values = last_question_number.copy()
    else:
        last_values = {}

    # 🔄 Réinitialiser uniquement les données journalières
    questions_today.clear()
    user_first_message_time.clear()

    # ✅ Restaurer les dernières valeurs de `last_question_number`
    last_question_number.clear()
    last_question_number.update(last_values)  # Restaure les dernières valeurs enregistrées

    logging.info("🔄 Réinitialisation quotidienne terminée avec conservation du dernier numéro de question.")

async def check_question_number(update: Update, context: CallbackContext) -> None:
    """Vérifie le premier message d'un utilisateur et ignore les suivants."""
    global last_reset_date

    if not update.message:
        return
        # 🔄 Vérification quotidienne pour réinitialiser `user_first_message_time` au début de chaque journée
        today = datetime.date.today()
        if today != last_reset_date:
            user_first_message_time.clear()  # 🔄 Réinitialise les participants de la veille
            last_reset_date = today
            logging.info("🔄 Réinitialisation quotidienne automatique des participants.")


    user = update.message.from_user
    message_text = update.message.text.strip()
    chat_id = update.message.chat_id
    mention = get_mention(user)
    user_id = user.id
    current_time = time.time()

    # ✅ Vérifier si le bot a déjà initialisé le dernier numéro pour ce groupe
    if chat_id not in last_question_number:
        await initialize_last_question_number(context, chat_id)

    # ✅ Ignorer si c'est une réponse à un autre message
    if update.message.reply_to_message:
        return

    # ✅ Vérifier si l'utilisateur est un simple membre (exclure admins)
    try:
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        if chat_member.status != "member":
            return  # Ignorer les admins et autres rôles
    except Exception as e:
        logging.error(f"❌ Erreur lors de la vérification du statut pour {user_id} : {e}")
        return

    # ✅ Si l'utilisateur a déjà été vérifié, on ignore tous ses messages suivants
    if user_id in user_first_message_time:
        return

    # ✅ Enregistrer la première participation de l'utilisateur
    user_first_message_time[user_id] = current_time

    # ✅ Vérifier si un `#` est présent dans le message
    match = re.search(r"#(\d+)", message_text)
    last_number = last_question_number.get(chat_id, 0)
    expected_number = last_number + 1  # Toujours avancer de `n + 1`

    if not match:
        # 🔴 Si pas de `#`, on force l'utilisateur à en mettre un et on avance immédiatement
        last_question_number[chat_id] = expected_number
        logging.warning(
            f"❗️ Message sans # détecté. Dernier numéro : {last_number}, Numéro attendu : {expected_number}")

        await update.message.reply_text(
            f"{mention} As-salam aleykoum, il semble que vous ayez oublié d'inclure un numéro de question. "
            f"Pourriez-vous, s'il vous plaît, ajouter #{expected_number} ? Baarak Allahu fik."
        )
    else:
        # ✅ Extraire le numéro de la question
        question_number = int(match.group(1))
        logging.info(
            f"🔍 Numéro détecté : {question_number}, Dernier numéro connu : {last_number}, Numéro attendu : {expected_number}")

        # 🔴 Si le numéro est déjà utilisé ou en retard, on propose le prochain et on avance immédiatement
        if question_number < last_number:
            last_question_number[chat_id] = expected_number
            logging.error(f"❌ Numéro déjà utilisé. Utilisateur : {mention}, Numéro utilisé : {question_number}, "
                          f"Numéro attendu : {expected_number}")

            await update.message.reply_text(
                f"{mention}  As-salam aleykoum, ce numéro semble déjà avoir été utilisé. "
                f"Je vous invite à utiliser plutôt #{expected_number}. Baarak Allahu fik."
            )

        # 🔴 Si l'utilisateur saute un numéro, on avance immédiatement et on propose le bon
        elif question_number > expected_number:
            last_question_number[chat_id] = expected_number
            logging.warning(f"⚠️ Numéro sauté. Utilisateur : {mention}, Numéro utilisé : {question_number}, "
                            f"Numéro attendu : {expected_number}")

            await update.message.reply_text(
                f"{mention} As-salam aleykoum, il semble que certains numéros aient été sautés. 😊 "
                f"Je vous invite à utiliser le numéro #{expected_number}. Baarak Allahu fik."
            )

        # ✅ Si tout est correct, on enregistre la question et on avance
        else:
            last_question_number[chat_id] = question_number
            logging.info(f"✅ Nouvelle question enregistrée : {mention} a utilisé #{question_number} dans {chat_id}")

    # ✅ Vérifier si on doit fermer le groupe après cette question
    #await check_and_close_group(update, context)

# ✅ Planification fiable avec `apscheduler`
def schedule_daily_reset():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(reset_daily_data, 'cron', hour=0, minute=0)  # Tous les jours à minuit
    scheduler.start()



# ✅ Fonction pour supprimer un message hors sujet avec /hs (réservé aux admins)
async def remove_off_topic(update: Update, context: CallbackContext) -> None:
    """Supprime un message hors sujet et aussi le message /hs de l'admin."""
    if update.message and update.message.reply_to_message:
        user = update.message.from_user  # L'admin ou l'utilisateur qui exécute la commande
        chat_id = update.message.chat_id
        message_to_delete = update.message.reply_to_message
        target_user = message_to_delete.from_user  # L'utilisateur dont le message est supprimé

        # ✅ Vérifier si l'utilisateur est un "member" (les autres statuts sont autorisés)
        try:
            chat_member = await context.bot.get_chat_member(chat_id, user.id)

            if chat_member.status == "member":
                await update.message.reply_text("❌ Seuls les admins peuvent utiliser cette commande.")
                return  # ❌ Bloquer uniquement les "members"

        except Exception as e:
            logging.error(f"❌ Erreur lors de la vérification du statut pour {user.id} : {e}")

        try:
            # ✅ Supprimer le message hors sujet
            await context.bot.delete_message(chat_id, message_to_delete.message_id)

            # ✅ Mentionner l'utilisateur concerné correctement
            mention = get_mention(target_user)

            # ✅ Envoyer un message expliquant la suppression
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ {mention}, *votre message a été supprimé car il est hors sujet.*\n\n"
                     "📌 **Seules les questions liées à la croyance, au fiqh malikite et à la spiritualité qui touchent votre quotidien sont autorisées.**\n"
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
    """Supprime un message si un admin utilise /waswas en réponse et informe l'utilisateur directement dans le groupe."""
    if update.message and update.message.reply_to_message:
        user = update.message.from_user  # L'admin ou la personne utilisant la commande
        chat_id = update.message.chat_id
        message_to_delete = update.message.reply_to_message
        target_user = message_to_delete.from_user  # Utilisateur dont le message est supprimé

        # ✅ Vérifier si l'utilisateur est un "member" (les autres statuts sont autorisés)
        try:
            chat_member = await context.bot.get_chat_member(chat_id, user.id)

            if chat_member.status == "member":
                await update.message.reply_text("❌ Seuls les admins peuvent utiliser cette commande.")
                return  # ❌ Bloquer uniquement les "members"

        except Exception as e:
            logging.error(f"❌ Erreur lors de la vérification du statut pour {user.id} : {e}")

        try:
            # ✅ Supprimer le message du membre contenant du waswas
            await context.bot.delete_message(chat_id, message_to_delete.message_id)

            # ✅ Mentionner l'utilisateur concerné correctement
            mention = get_mention(target_user)

            # ✅ Envoyer un message expliquant la suppression
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ {mention}, *votre message a été supprimé, car il pourrait causer des wasâwis aux autres membres* \n\n"
                     f"(doutes maladifs nuisant à la pratique religieuse).\n\n"
                     "📌 *Veuillez poser votre question en privé à  @questionsprivees.*\n"
                     "Merci de votre compréhension.",
                parse_mode="Markdown"
            )

            # ✅ Supprimer le message de l'admin contenant /waswas
            await context.bot.delete_message(chat_id, update.message.message_id)

        except Exception as e:
            logging.error(f"Erreur lors de la suppression du message de waswas : {e}")
            await update.message.reply_text("❌ Impossible de supprimer ce message.")

async def remove_private_message(update: Update, context: CallbackContext) -> None:
    """Supprime un message si un admin utilise /priver en réponse et informe l'utilisateur directement dans le groupe."""
    if update.message and update.message.reply_to_message:
        user = update.message.from_user  # L'admin ou la personne utilisant la commande
        chat_id = update.message.chat_id
        message_to_delete = update.message.reply_to_message
        target_user = message_to_delete.from_user  # Utilisateur dont le message est supprimé

        # ✅ Vérifier si l'utilisateur est un "member" (les autres statuts sont autorisés)
        try:
            chat_member = await context.bot.get_chat_member(chat_id, user.id)
            if chat_member.status == "member":
                return  # ❌ Bloquer uniquement les "members"

        except Exception as e:
            logging.error(f"❌ Erreur lors de la vérification du statut pour {user.id} : {e}")
            return

        try:
            # ✅ Supprimer le message du membre contenant la question privée
            await context.bot.delete_message(chat_id, message_to_delete.message_id)

            # ✅ Mentionner l'utilisateur concerné correctement
            mention = get_mention(target_user)

            # ✅ Envoyer un message expliquant la suppression
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ {mention}, *votre question semble privée ou expose potentiellement des péchés.*\n\n"
                     "📌 *Je vous invite à poser votre question en privé à @questionsprivees.*\n"
                     "Nous vous remercions pour votre compréhension.",
                parse_mode="Markdown"
            )

            # ✅ Supprimer le message de l'admin contenant /priver
            await context.bot.delete_message(chat_id, update.message.message_id)

        except Exception as e:
            logging.error(f"❌ Erreur lors de la suppression du message privé : {e}")
            await update.message.reply_text("❌ Impossible de supprimer ce message.")



# /jeune
async def send_fasting_info(update: Update, context: CallbackContext) -> None:
    """Envoie une réponse automatique sur le fiqh du jeûne lorsque /jeune est utilisé en réponse."""

    if update.message and update.message.reply_to_message:
        user = update.message.from_user
        chat_id = update.message.chat_id
        message_to_reply = update.message.reply_to_message

        # ✅ Vérifier si l'utilisateur est un "member" (les autres statuts sont autorisés)
        try:
            chat_member = await context.bot.get_chat_member(chat_id, user.id)

            if chat_member.status == "member":
                await update.message.reply_text("❌ Seuls les admins peuvent utiliser cette commande.")
                return  # ❌ Bloquer uniquement les "members"

        except Exception as e:
            logging.error(f"❌ Erreur lors de la vérification du statut pour {user.id} : {e}")

        try:
            # ✅ Obtenir la mention de l'utilisateur mentionné
            mention = get_mention(message_to_reply.from_user)

            # ✅ Envoyer la réponse automatique
            await context.bot.send_message(
                chat_id=chat_id,
                reply_to_message_id=message_to_reply.message_id,
                text=f"As-salam aleykoum {mention}, votre question laisse entendre que vous n'avez pas encore étudié "
                     "le fiqh du jeûne de façon systématique en suivant un cours sur le sujet ou, du moins, "
                     "qu'une révision du sujet vous serait bénéfique.\n\n"
                     "📌 *Voici un mini-cours gratuit sans inscription qui vous permettra de vous acquitter de cette obligation :* \n"
                     "👉 [Épitre du Jeûne](https://majlisalfatih.weebly.com/epitre-du-jeune.html)\n\n"
                     " Baraak Allahu fik !",
                parse_mode="Markdown"
            )

            # ✅ Supprimer la commande /jeune après envoi du message
            await update.message.delete()

        except Exception as e:
            logging.error(f"❌ Erreur lors de l'envoi du message /jeune : {e}")
            await update.message.reply_text("❌ Impossible d'envoyer le message.")


# ✅ Ajouter la commande au gestionnaire

async def remove_excess_question(update: Update, context: CallbackContext) -> None:
    """Supprime une question en trop et ajuste la numérotation pour éviter les erreurs."""
    if update.message and update.message.reply_to_message:
        user = update.message.from_user  # L'admin qui exécute la commande
        chat_id = update.message.chat_id
        message_to_delete = update.message.reply_to_message
        target_user = message_to_delete.from_user  # L'utilisateur dont la question est supprimée
        message_text = message_to_delete.text.strip()  # Texte du message supprimé

        # ✅ Vérifier si l'utilisateur est admin (empêcher les "members" d'utiliser la commande)
        try:
            chat_member = await context.bot.get_chat_member(chat_id, user.id)

            if chat_member.status == "member":
                await update.message.reply_text("❌ Seuls les admins peuvent utiliser cette commande.")
                return  # ❌ Bloquer uniquement les "members"

        except Exception as e:
            logging.error(f"❌ Erreur lors de la vérification du statut pour {user.id} : {e}")

        try:
            # ✅ Vérifier si un numéro de question est présent
            match = re.search(r"#(\d+)", message_text)
            if match:
                question_number = int(match.group(1))

                # ✅ Vérifier si la question supprimée est la dernière enregistrée
                if last_question_number.get(chat_id) == question_number:
                    last_question_number[chat_id] -= 1  # Décrémenter pour éviter les sauts de numéros

            # ✅ Supprimer le message en trop
            await context.bot.delete_message(chat_id, message_to_delete.message_id)

            # ✅ Mentionner l'utilisateur concerné
            mention = get_mention(target_user)

            # ✅ Envoyer un message expliquant la suppression
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ {mention}, une seule question par membre par jour est autorisée.\n\n"
                     "❌ Votre question a été supprimée automatiquement.\n"
                     "🚨 S'il s'agit d'une urgence, veuillez envoyer votre question au compte @questionsprivees.",
                parse_mode="Markdown"
            )

            # ✅ Supprimer aussi le message de l'admin contenant /1
            await context.bot.delete_message(chat_id, update.message.message_id)

        except Exception as e:
            logging.error(f"Erreur lors de la suppression de la question en trop : {e}")
            await update.message.reply_text("❌ Impossible de supprimer ce message.")
users_who_asked_today = {}  # Dictionnaire qui stocke les utilisateurs ayant posé une question aujourd'hui


# ✅ Dictionnaire pour stocker les questions du jour

# async def check_and_close_group(update: Update, context: CallbackContext) -> None:
#     """Ferme le groupe si 10 questions ont été posées dans la journée."""
#     global questions_today, users_who_asked_today  # Ajout de la nouvelle liste
#
#     if not update.message or not update.message.text:
#         return
#
#     user_id = update.message.from_user.id
#     chat_id = update.message.chat_id
#     today = datetime.date.today()
#
#     # ✅ Vérifier si c'est une nouvelle journée (reset du compteur)
#     if chat_id not in questions_today or questions_today[chat_id]["date"] != today:
#         questions_today[chat_id] = {"count": 0, "date": today}
#         users_who_asked_today[chat_id] = set()  # Réinitialiser la liste des utilisateurs du jour
#         logging.info(f"🔄 Réinitialisation du compteur de questions pour le groupe {chat_id}.")
#
#     # ✅ Vérifier si l'utilisateur a déjà posé une question aujourd'hui
#     if user_id not in users_who_asked_today[chat_id]:  # 🚀 Si c'est son premier message du jour
#         questions_today[chat_id]["count"] += 1
#         count = questions_today[chat_id]["count"]
#         logging.info(f"📊 Nombre de questions posées aujourd'hui dans {chat_id} : {count}")
#
#         # ✅ Ajouter l'utilisateur à la liste des utilisateurs ayant posé une question aujourd'hui
#         users_who_asked_today[chat_id].add(user_id)
#
#     # ✅ Vérifier si la limite de 10 questions est atteinte
#     if questions_today[chat_id]["count"] >= 10:
#         logging.warning(f"🚨 Limite de 10 questions atteinte dans {chat_id}. Fermeture du groupe.")
#         await close_group_until_midnight(update, context)


# async def close_group_until_midnight(update: Update, context: CallbackContext) -> None:
#     """Ferme le groupe jusqu'à minuit."""
#     chat_id = update.message.chat_id
#
#     try:
#         # 🔒 Bloquer l'envoi de messages
#         await context.bot.set_chat_permissions(
#             chat_id=chat_id,
#             permissions=ChatPermissions( can_send_messages=False,      # 🔴 Bloque l'envoi de messages
#                 can_send_other_messages=False )
#         )
#
#         # 📢 Envoyer un message d'information
#         await update.message.reply_text(
#             "⚠️ *La limite de 10 questions a été atteinte pour aujourd’hui.*\n\n"
#             "📌 *Le groupe est fermé jusqu'à minuit.*\n"
#             "📌 *En cas d’urgence, contactez @questionsprivees.*",
#             parse_mode="Markdown"
#         )
#
#         logging.info(f"🔒 Groupe {chat_id} fermé jusqu'à minuit.")
#
#         # ✅ Réinitialiser immédiatement le compteur de questions
#         questions_today[chat_id] = {"count": 0, "date": datetime.date.today()}
#         logging.info(f"🔄 Réinitialisation immédiate du compteur pour {chat_id}.")
#
#         # ⏳ Calcul du temps restant jusqu'à minuit
#         now = datetime.datetime.now()
#         reopen_time = datetime.datetime.combine(now.date(), datetime.time(23, 59))
#         seconds_until_reopen = (reopen_time - now).total_seconds()
#
#         # ✅ Planifier la réouverture du groupe à minuit
#         asyncio.create_task(reopen_group_at_2359(chat_id, context, seconds_until_reopen))
#
#     except Exception as e:
#         logging.error(f"❌ Erreur lors de la fermeture du groupe : {e}")


async def reopen_group_at_2359(chat_id, context, delay):
    """Attend jusqu'à 23h59 et réactive les messages."""
    await asyncio.sleep(delay)  # Attendre jusqu'à 23h59

    try:
        # 🔓 Réactiver les messages
        await context.bot.set_chat_permissions(
            chat_id=chat_id,
            permissions=ChatPermissions(can_send_messages=True)
        )

        # 📢 Envoyer un message de réouverture
        await context.bot.send_message(
            chat_id=chat_id,
            text="✅ *Les questions sont à nouveau ouvertes !* Vous pouvez poser vos questions.",
            parse_mode="Markdown"
        )

        # 🎯 Réinitialiser le compteur pour la nouvelle journée
        questions_today[chat_id] = {"count": 0, "date": datetime.date.today()}
        logging.info(f"✅ Groupe {chat_id} rouvert, compteur réinitialisé.")

    except Exception as e:
        logging.error(f"❌ Erreur lors de la réouverture du groupe : {e}")


async def ban_user(update: Update, context: CallbackContext) -> None:
    """Bannit un utilisateur du groupe si un admin utilise /ban en réponse à un message."""
    if update.message and update.message.reply_to_message:
        admin = update.message.from_user
        chat_id = update.message.chat_id
        target_user = update.message.reply_to_message.from_user

        # Vérifier si l'utilisateur qui exécute la commande est un admin
        chat_member = await context.bot.get_chat_member(chat_id, admin.id)
        if chat_member.status not in ["administrator", "creator"]:
            await update.message.reply_text("❌ Seuls les administrateurs peuvent utiliser cette commande.")
            return

        try:
            # Bannir l'utilisateur
            await context.bot.ban_chat_member(chat_id, target_user.id)

            # Supprimer le message de l'admin contenant la commande /ban
            await update.message.delete()

            # Obtenir la mention correcte de l'utilisateur banni
            mention = get_mention(target_user)

            # Envoyer un message de confirmation dans le groupe
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🚫 {mention} a été banni du groupe par un administrateur.",
                parse_mode="MarkdownV2"
            )

        except Exception as e:
            logging.error(f"Erreur lors de l'exclusion de l'utilisateur : {e}")
            await update.message.reply_text("❌ Impossible de bannir cet utilisateur.")

    else:
        await update.message.reply_text(
            "❌ Utilisation incorrecte. Répondez à un message avec `/ban` pour bannir un utilisateur.")


async def unclear_question(update: Update, context: CallbackContext) -> None:
    """Indique qu'une question n'est pas claire et demande à l'utilisateur de la reformuler."""
    if update.message and update.message.reply_to_message:
        user = update.message.from_user  # L'admin qui exécute la commande
        chat_id = update.message.chat_id
        target_message = update.message.reply_to_message
        target_user = target_message.from_user  # L'utilisateur qui a posé la question

        # ✅ Vérifier si l'utilisateur est un admin (empêcher les "members" d'utiliser la commande)
        try:
            chat_member = await context.bot.get_chat_member(chat_id, user.id)

            if chat_member.status == "member":
                await update.message.reply_text("❌ Seuls les admins peuvent utiliser cette commande.")
                return  # ❌ Bloquer uniquement les "members"

        except Exception as e:
            logging.error(f"❌ Erreur lors de la vérification du statut pour {user.id} : {e}")

        try:
            # ✅ Mentionner l'utilisateur concerné
            mention = get_mention(target_user)

            # ✅ Envoyer un message d'avertissement sans supprimer son message
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Wa'alaykumus-salaam {mention},\n\n"
                     "❌ Votre question n'est pas claire.\n"
                     "📌 Veuillez la reformuler en modifiant votre message.",
                parse_mode="Markdown"
            )

            # ✅ Supprimer le message de l'admin contenant /pc
            try:
                await update.message.delete()
            except Exception as e:
                logging.error(f"❌ Impossible de supprimer le message de commande /pc : {e}")

        except Exception as e:
            logging.error(f"Erreur lors de l'envoi du message /pc : {e}")
            await update.message.reply_text("❌ Impossible d'envoyer l'avertissement.")


# Remplace `CHAT_ID` par l'ID de ton groupe

async def correction(update: Update, context: CallbackContext) -> None:
    """Décrémente le dernier numéro de question manuellement via la commande /correction avec vérification admin."""
    if not update.message:
        return

    user = update.message.from_user
    chat_id = update.message.chat_id

    # ✅ Vérifier si l'utilisateur est un admin
    try:
        chat_member = await context.bot.get_chat_member(chat_id, user.id)
        if chat_member.status == "member":
            await update.message.reply_text("❌")
            return
    except Exception as e:
        logging.error(f"❌ Erreur lors de la vérification du statut pour {user.id} : {e}")
        return

    # ✅ Décrémenter le dernier numéro de question
    if chat_id in last_question_number and last_question_number[chat_id] > 0:
        last_question_number[chat_id] -= 1
        logging.info(
            f"➖ Décrément manuel dans le groupe {chat_id}. Nouveau dernier numéro : #{last_question_number[chat_id]}")

    # ✅ Supprimer immédiatement le message de l'admin
    try:
        await update.message.delete()
    except Exception as e:
        logging.error(f"❌ Impossible de supprimer le message de commande /correction : {e}")




async def plus(update: Update, context: CallbackContext) -> None:
    """Incrémente le dernier numéro de question manuellement via la commande /plus avec vérification admin."""
    if not update.message:
        return

    user = update.message.from_user
    chat_id = update.message.chat_id

    # ✅ Vérifier si l'utilisateur est un admin
    try:
        chat_member = await context.bot.get_chat_member(chat_id, user.id)
        if chat_member.status == "member":
            await update.message.reply_text("❌")
            return
    except Exception as e:
        logging.error(f"❌ Erreur lors de la vérification du statut pour {user.id} : {e}")
        return

    # ✅ Incrémenter le dernier numéro de question
    if chat_id not in last_question_number:
        last_question_number[chat_id] = 0

    last_question_number[chat_id] += 1
    logging.info(f"➕ Incrément manuel dans le groupe {chat_id}. Nouveau dernier numéro : #{last_question_number[chat_id]}")

    # ✅ Supprimer immédiatement le message de l'admin
    try:
        await update.message.delete()
    except Exception as e:
        logging.error(f"❌ Impossible de supprimer le message de commande /plus : {e}")


# ✅ Ajouter le handler de la commande /plus

async def send_daily_message(context: CallbackContext) -> None:
    """Envoie un message quotidien à 00h01."""
    message = (
        "Nous nous retrouvons ce jour par la Grâce d'Allah dans Q&R MALIKIYYAH, "
        "groupe dédié aux questions pratiques de fiqh, de 'aqiidah et de tasawwuf de la communauté musulmane ⭐️\n\n"
        "📌 **RAPPEL GÉNÉRAL** 📌\n\n"
        "▪️ Respectez les [règles du groupe](https://t.me/c/1912372093/7898) \n"
        "▪️ Et surtout : étudiez la Science !\n"
        "👉 Remplissez cette obligation en suivant [des cours](https://majlisalfatih.weebly.com/cours.html)\n\n"
        "Baraak Allaahu fiikum !"
    )

    try:
        await context.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
        logging.info("✅ Message quotidien envoyé avec succès.")
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'envoi du message quotidien : {e}")


def schedule_daily_message(application: Application) -> None:
    """Planifie l'envoi du message quotidien à 00h01."""
    job_queue = application.job_queue
    now = datetime.datetime.now()
    midnight = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0, 1))

    # Calcul du temps restant jusqu'à 00h01
    delay = (midnight - now).total_seconds()

    # Planifier l'exécution quotidienne
    job_queue.run_daily(send_daily_message, time=datetime.time(0, 1), chat_id=CHAT_ID)

    logging.info("✅ Message quotidien planifié pour 00h01.")


CHAT_IDtest = -1002391499606  # Remplace par l'ID du canal où tu veux exécuter la tâche


async def keep_bot_active(context: CallbackContext) -> None:
    """Tâche exécutée toutes les 3 minutes uniquement dans un canal spécifique."""
    try:
        await context.bot.send_message(
            chat_id=CHAT_IDtest,
            text="🔄 Le bot est actif.",
        )
        logging.info("✅ Message anti-sleep envoyé.")
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'envoi du message anti-sleep : {e}")


# ✅ Fonction principale
def main():
    keep_alive()  # Garde le bot en ligne

    logging.info("Démarrage du bot...")

    app = Application.builder().token(TOKEN).build()
    # ✅ Planifier la tâche toutes les 3 minutes UNIQUEMENT sur le canal défini
    job_queue = app.job_queue
    job_queue.run_repeating(keep_bot_active, interval=400, first=10)  # 🔄 Exécution toutes les 3 minutes

    # message quotidien
    schedule_daily_message(app)

    #

    # Gestion des nouveaux membres
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

    # Vérification du format et de l'ordre des questions
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_question_number))
    logging.info("✅ Handler `welcome_new_member` ajouté avec succès.")

    app.add_handler(CommandHandler("1", remove_excess_question))
    app.add_handler(CommandHandler("correction", correction))
    app.add_handler(CommandHandler("plus", plus))
    app.add_handler(CommandHandler("priver", remove_private_message))
    app.add_handler(CommandHandler("pc", unclear_question))

    # Vérification de l'acceptation des règles
    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_acceptance))

    # fonction hs
    app.add_handler(CommandHandler("hs", remove_off_topic))

    # wawas
    app.add_handler(CommandHandler("waswas", remove_waswas_message))

    # app.add_handler(CommandHandler("10", close_group_for_6h))

    #app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_and_close_group))

    app.add_handler(CommandHandler("ban", ban_user))

    app.add_handler(CommandHandler("dr", already_answered))
    app.add_handler(CommandHandler("jeune", send_fasting_info))

    # boutton
    app.add_handler(CallbackQueryHandler(button_click, pattern=r"^accept_\d+$"))

    # Lancer le bot
    app.run_polling()
    asyncio.create_task(schedule_daily_reset(app))


if __name__ == "__main__":
    main()
