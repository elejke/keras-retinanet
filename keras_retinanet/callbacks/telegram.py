import threading

from keras.callbacks import Callback


# custom telegram logger callback:
class TelegramCallback(Callback):
    def __init__(self, model_name, config):
        super().__init__()
        self.model_name = model_name
        self.config = config
        self.telegram_logger = TelegramLogger(self.config)

        self.telegram_logger.log(self.model_name + " model training started.")

    def on_epoch_end(self, epoch, logs={}):
        try:
            self.telegram_logger.log("Model: " + self.model_name + ":\n loss: " + str(logs.get('loss')) +
                                     ";\n regression_loss: " + str(logs.get('regression_loss')) +
                                     ";\n classification_loss: " + str(logs.get('classification_loss')))
        except:
            print("No response from proxy server")


class TelegramLogger(threading.Thread):
    """ Logger which redirects all the incoming messages into specified telegram bot.
    """

    def __init__(self, config, use_proxy=False):
        """ Constructor. Create TeleBot instance and launch it in the separate thread.
        Args:
            config(dict): dict with the telegram bot token and default chat id
        Return:
            None
        """
        # parent constructor
        super(TelegramLogger, self).__init__()
        # import telegram bot api:
        import telebot

        self.config = config
        self.use_proxy = use_proxy
        if self.use_proxy:
            from telebot import apihelper
            apihelper.proxy = {'https': 'socks5://' + str(self.config["proxy_ip"]) + ':' + str(self.config["proxy_port"])}
        # create bot
        self._bot = telebot.TeleBot(self.config["token"])
        # chat id to send messages to
        self._cids = {self.config['cid']}

        # start bot in a separate thread
        self.start()

    def run(self):
        """Override of standard Thread class function to be able to run bot polling in separate thread.
        Return:
            None
        """
        self._create_bot()

    def _create_bot(self):
        """ Create message handlers and then start bot.
        Return:
            None
        """

        @self._bot.message_handler(commands=["start"])
        def _start_msg(message):
            """ Answer to /start message. Append chat to the list of broadcast chats.
            Args:
                message(telebot.Message): incoming message
            Return:
                None
            """
            # add chat to the list of chats for broadcast
            self._cids.add(message.chat.id)
            # send answer
            self._bot.send_message(message.chat.id, "Hello there!")

        @self._bot.message_handler(commands=["stop"])
        def _stop_msg(message):
            """ Answer to /stop message. Delete chat from the list of broadcast chats.
            Args:
                message(telebot.Message): incoming message
            Return:
                None
            """
            # remove chat from the list of chats for broadcast
            self._cids.discard(message.chat.id)
            # send answer
            self._bot.send_message(message.chat.id, "I'll be back.")

        @self._bot.message_handler(commands=["help"])
        def _help_msg(message):
            """ Answer to /help message.  Append chat to the list of broadcast chats.
            Args:
                message(telebot.Message): incoming message
            Return:
                None
            """
            # add chat to the list of chats for broadcast
            self._cids.add(message.chat.id)
            # send answer
            self._bot.send_message(message.chat.id, "This bot is only for logging and is not interactive.")

        @self._bot.message_handler(func=lambda m: True)
        def _all_msg():
            """ No answer to all other messages.
            Return:
                None
            """
            pass

        # start the bot
        self._bot.polling(timeout=30)

    def log(self, message):
        """ Send the message to the bot.
        Args:
            message(str): info to send to the bot
        Return:
            None
        """
        for cid in self._cids:
            self._bot.send_message(cid, message)

    def close(self):
        """ Stop sending messages to everyone.
        Return:
            None
        """
        self._cids = {}
