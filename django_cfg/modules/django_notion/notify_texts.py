"""Words of the acknowledgement letter ("we received your request"), per language. English is the fallback.

``{project}`` / ``{within}`` / ``{name}`` are filled by ``notify``. Keep the sentences short: the letter is an auto-reply.
"""

from __future__ import annotations

from typing import Optional

DEFAULT = "en"

TEXTS = {
    "en": {
        "subject": "We received your request — {project}",
        "hello": "Hello", "hello_name": "Hello, {name}",
        "body": "Thank you. We received your request and will get back to you soon.",
        "within": "We usually reply within {within}.",
        "recap": "Your request", "form": "Subject", "message": "Message",
        "reply": "You can reply to this email to add details.",
    },
    "ru": {
        "subject": "Мы получили ваше обращение — {project}",
        "hello": "Здравствуйте", "hello_name": "Здравствуйте, {name}",
        "body": "Спасибо. Мы получили ваше обращение и скоро ответим.",
        "within": "Обычно мы отвечаем в течение {within}.",
        "recap": "Ваше обращение", "form": "Тема", "message": "Сообщение",
        "reply": "Чтобы добавить подробности, просто ответьте на это письмо.",
    },
    "ko": {
        "subject": "문의가 접수되었습니다 — {project}",
        "hello": "안녕하세요", "hello_name": "안녕하세요, {name}님",
        "body": "감사합니다. 문의를 접수했으며 곧 답변드리겠습니다.",
        "within": "보통 {within} 이내에 답변드립니다.",
        "recap": "문의 내용", "form": "제목", "message": "메시지",
        "reply": "추가 내용은 이 메일에 회신해 주세요.",
    },
    "de": {
        "subject": "Wir haben Ihre Anfrage erhalten — {project}",
        "hello": "Guten Tag", "hello_name": "Guten Tag, {name}",
        "body": "Vielen Dank. Wir haben Ihre Anfrage erhalten und melden uns in Kürze.",
        "within": "In der Regel antworten wir innerhalb von {within}.",
        "recap": "Ihre Anfrage", "form": "Betreff", "message": "Nachricht",
        "reply": "Antworten Sie einfach auf diese E-Mail, um Details zu ergänzen.",
    },
    "fr": {
        "subject": "Nous avons bien reçu votre demande — {project}",
        "hello": "Bonjour", "hello_name": "Bonjour {name}",
        "body": "Merci. Nous avons bien reçu votre demande et reviendrons vers vous rapidement.",
        "within": "Nous répondons généralement sous {within}.",
        "recap": "Votre demande", "form": "Objet", "message": "Message",
        "reply": "Répondez à cet e-mail pour ajouter des précisions.",
    },
    "es": {
        "subject": "Hemos recibido tu solicitud — {project}",
        "hello": "Hola", "hello_name": "Hola, {name}",
        "body": "Gracias. Hemos recibido tu solicitud y te responderemos pronto.",
        "within": "Normalmente respondemos en {within}.",
        "recap": "Tu solicitud", "form": "Asunto", "message": "Mensaje",
        "reply": "Puedes responder a este correo para añadir detalles.",
    },
    "pt": {
        "subject": "Recebemos o seu pedido — {project}",
        "hello": "Olá", "hello_name": "Olá, {name}",
        "body": "Obrigado. Recebemos o seu pedido e responderemos em breve.",
        "within": "Normalmente respondemos em {within}.",
        "recap": "O seu pedido", "form": "Assunto", "message": "Mensagem",
        "reply": "Responda a este e-mail para acrescentar detalhes.",
    },
    "zh": {
        "subject": "我们已收到您的请求 — {project}",
        "hello": "您好", "hello_name": "{name}，您好",
        "body": "谢谢。我们已收到您的请求，会尽快回复您。",
        "within": "我们通常会在{within}内回复。",
        "recap": "您的请求", "form": "主题", "message": "留言",
        "reply": "如需补充信息，请直接回复此邮件。",
    },
    "ja": {
        "subject": "お問い合わせを受け付けました — {project}",
        "hello": "こんにちは", "hello_name": "{name}様",
        "body": "ありがとうございます。お問い合わせを受け付けました。まもなくご連絡いたします。",
        "within": "通常、{within}以内にご返信します。",
        "recap": "お問い合わせ内容", "form": "件名", "message": "メッセージ",
        "reply": "補足がある場合は、このメールにご返信ください。",
    },
    "ar": {
        "subject": "لقد استلمنا طلبك — {project}",
        "hello": "مرحباً", "hello_name": "مرحباً {name}",
        "body": "شكراً لك. لقد استلمنا طلبك وسنرد عليك قريباً.",
        "within": "نرد عادةً خلال {within}.",
        "recap": "طلبك", "form": "الموضوع", "message": "الرسالة",
        "reply": "يمكنك الرد على هذه الرسالة لإضافة تفاصيل.",
    },
}


def pick(locale: Optional[str]) -> str:
    """Language code for a locale tag (``ko-KR`` -> ``ko``); unknown or empty -> English."""
    base = str(locale or "").strip().replace("_", "-").split("-")[0].split(",")[0].split(";")[0].lower()
    return base if base in TEXTS else DEFAULT
