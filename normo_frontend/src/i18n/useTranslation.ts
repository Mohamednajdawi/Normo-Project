import { translations } from './translations';

type TranslationKey = keyof typeof translations.de;
type StringTranslationKey = Exclude<TranslationKey, 'exampleQuestions'>;

export const useTranslation = () => {
  const t = (key: StringTranslationKey): string => {
    const value = translations.de[key];
    return typeof value === 'string' ? value : String(value);
  };

  const tArray = (key: 'exampleQuestions'): string[] => {
    return translations.de[key] as string[];
  };

  return { t, tArray };
};

