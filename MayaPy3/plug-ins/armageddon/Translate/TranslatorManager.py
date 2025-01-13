from . import TranslateText

class TranslatorManager:
    def __init__(self):
        self.language = "zh"
        self.language_dict = TranslateText.TRANSLATE_TEXT
        self.object_dict = {}
        self.item_parents = []

    def getTranslatedText(self, source_text, lang_text):
        # print(source_text)
        trans_dict = self.language_dict.get(source_text)
        if trans_dict is None:
            return source_text

        trans_text = trans_dict.get(lang_text)
        if trans_text is None:
            return source_text

        return trans_text

    def switchToLang(self, language:str):
        if self.language == language:
            return
        self.language = language
        for key in self.object_dict.keys():
            try:
                key(self.getTranslatedText(self.object_dict[key], language))
            except BaseException as e:
                pass
            #     print(e)
        for item_parent in self.item_parents:
            for i in range(item_parent.count()):
                try:
                    source_text = item_parent.itemData(i)
                except BaseException as e:
                    break
                trans_text = self.getTranslatedText(source_text, language)
                item_parent.setItemText(i, trans_text)

    def switchToChinese(self):
        self.switchToLang("zh")

    def switchToEnglish(self):
        self.switchToLang("en")

    def addTranslate(self, text_method, text:str):
        self.object_dict.update({text_method: text})
        text_method(self.getTranslatedText(text, self.language))

    def addItemTranslate(self, item_parent):
        self.item_parents.append(item_parent)
        for i in range(item_parent.count()):
            source_text = item_parent.itemData(i)
            trans_text = self.getTranslatedText(source_text, self.language)
            item_parent.setItemText(i, trans_text)

    def switchLanguage(self):
        if self.language == "en":
            self.switchToChinese()
        elif self.language == "zh":
            self.switchToEnglish()

    def clear(self):
        self.object_dict.clear()
        self.item_parents.clear()


__translator = TranslatorManager()

def getTranslator():
    return __translator

def resetTranslator():
    __translator.clear()

def switchLanguage():
    __translator.switchLanguage()