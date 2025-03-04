import os
import time

from dotenv import load_dotenv
import aiocron
import datetime
import asyncio
from telegram import ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler
from keep_alive import keep_alive
import re


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


group_ids = set()  # Stocker dynamiquement les ID des groupes

async def track_group(update: Update, context: CallbackContext) -> None:
    """Ajoute dynamiquement les groupes où le bot est présent."""
    chat = update.message.chat
    if chat.type in ["group", "supergroup"]:
        group_ids.add(chat.id)
        logging.info(f"📌 Le bot a été ajouté dans le groupe : {chat.title} (ID: {chat.id})")

import re

def get_mention(user):
    """Retourne @username si disponible, sinon affiche juste le prénom/nom sans lien."""
    if user.username:
        return f"@{user.username}"  # ✅ Affiche l'@username normalement
    else:
        # ✅ Affiche uniquement le prénom/nom sans lien, sans caractères spéciaux MarkdownV2
        first_name = user.first_name if user.first_name else "Utilisateur"
        clean_name = re.sub(r"([_*[\]()~`>#+-=|{}.!])", r"\\\1", first_name)  # Échapper MarkdownV2

        return clean_name  # ✅ Juste le nom/prénom, sans lien Telegram


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



async def check_question_number(update: Update, context: CallbackContext) -> None:
    """Vérifie si un message contient un numéro de question valide (#XXX) et suit l'ordre strict."""

    if not update.message:
        return

    user = update.message.from_user
    message_text = update.message.text.strip()  # Supprimer les espaces inutiles
    chat_id = update.message.chat_id
    mention = get_mention(user)
    user_id = user.id
    current_time = time.time()

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

    # ✅ Vérifier si l'utilisateur a récemment posé une question (moins de 15 min)
    last_time = user_last_question_time.get(user_id, 0)
    if current_time - last_time < 1:  # ⏳ 15 minutes = 900 secondes
        return  # Ignorer les messages de cet utilisateur s'il a déjà posé une question récemment

    # ✅ Vérifier si un `#` est présent dans le message
    match = re.search(r"#(\d+)", message_text)

    if not match:
        last_number = last_question_number.get(chat_id, 0)
        expected_number = last_number + 1

        # 🔴 Correction : Incrémenter immédiatement pour éviter les conflits
        last_question_number[chat_id] = expected_number

        await update.message.reply_text(
            f"{mention} Veuillez inclure un numéro de question avec #{expected_number}."

        )
        return

    # ✅ Extraire le numéro de la question
    question_number = int(match.group(1))

    # ✅ Récupérer le dernier numéro de question pour ce chat
    last_number = last_question_number.get(chat_id, 0)
    expected_number = last_number + 1

    # ✅ Vérifier si le bot démarre en cours de route (ex: le groupe est déjà à #1400)
    if chat_id not in last_question_number:
        last_question_number[chat_id] = question_number
        user_last_question_time[user_id] = current_time
        return

    # ✅ Vérifier que la numérotation suit bien l’ordre séquentiel
    if question_number < expected_number:
        await update.message.reply_text(
            f"{mention} Ce numéro est déjà utilisé. Veuillez utiliser #{expected_number}."
        )
        return

    if question_number > expected_number:
        await update.message.reply_text(
            f"{mention} Vous avez sauté des numéros ! Le bon numéro est #{expected_number}."
        )
        # 🔴 On incrémente directement le dernier numéro pour éviter les conflits
        last_question_number[chat_id] += 1
        return

    # ✅ Mettre à jour avec le dernier numéro
    last_question_number[chat_id] = question_number
    user_last_question_time[user_id] = current_time  # Mise à jour du timestamp utilisateur

    await check_and_close_group(update, context)  # Vérifier si la limite de 10 questions est atteinte


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




#/jeune
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

# Ajouter cette commande au dispatcher

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
        await update.message.reply_text("❌ Utilisation incorrecte. Répondez à un message avec `/ban` pour bannir un utilisateur.")




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
CHAT_ID =-1001912372093   # ⚠️ Remplace avec l'ID réel de ton groupe




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
    job_queue.run_repeating(keep_bot_active, interval=180, first=10)  # 🔄 Exécution toutes les 3 minutes

    #message quotidien
    schedule_daily_message(app)

    #
    app.add_handler(CommandHandler("start", start))

    # Gestion des nouveaux membres
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

    # Vérification du format et de l'ordre des questions
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_question_number))

    app.add_handler(CommandHandler("1", remove_excess_question))

    app.add_handler(CommandHandler("pc", unclear_question))

    # Vérification de l'acceptation des règles
    #app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_acceptance))

    # fonction hs
    app.add_handler(CommandHandler("hs", remove_off_topic))

    # wawas
    app.add_handler(CommandHandler("waswas", remove_waswas_message))

    # app.add_handler(CommandHandler("10", close_group_for_6h))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_and_close_group))

    app.add_handler(CommandHandler("ban", ban_user))

    app.add_handler(CommandHandler("dr", already_answered))
    app.add_handler(CommandHandler("jeune", send_fasting_info))

    #boutton
    app.add_handler(CallbackQueryHandler(button_click, pattern=r"^accept_\d+$"))

    # Lancer le bot
    app.run_polling()


if __name__ == "__main__":
    main()
