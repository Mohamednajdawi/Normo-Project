// German translations for Normo Frontend
export const translations = {
  de: {
    // ChatInterface
    appTitle: "Normo Baurecht Assistent",
    continuingConversation: "Das Gespräch fortsetzen - Folgefragen stellen",
    askAboutBuildingCodes: "Fragen Sie zu Bauvorschriften, Verordnungen und architektonischen Anforderungen",
    conversationId: "Gespräch ID",
    welcomeTitle: "Willkommen beim Normo Baurecht Assistent",
    welcomeDescription: "Ihr KI-gestützter Assistent für österreichische Bauvorschriften. Stellen Sie Fragen zu Spielplatzanforderungen, Gebäudehöhen, Baustandards und mehr. Erhalten Sie genaue Berechnungen mit rechtlichen Zitaten.",
    tryTheseExamples: "Versuchen Sie diese Beispiele:",
    exampleQuestions: [
      "Ich baue ein Wohngebäude mit 5 Wohnungen in Linz. Wie viele Quadratmeter Spielplatz muss ich planen?",
      "Was sind die Gebäudehöhenanforderungen im österreichischen Recht?",
      "Welche Abfallwirtschaftsregelungen gelten in Oberösterreich?",
      "Was sind die Raumhöhenanforderungen für Wohngebäude?",
    ] as string[],
    analyzingDocuments: "Österreichische Rechtsdokumente werden analysiert...",
    inputPlaceholder: "Stell eine Frage zum österreichischen Baurecht.",
    inputHelper: "Enter zum Senden, Shift + Enter für neue Zeile",
    
    // Sidebar
    newChat: "Neue Chat",
    sidebarTitle: "Normo Baurecht Assistent",
    sidebarDescription: "KI-gestützter Assistent für österreichische Bauvorschriften",
    recentConversations: "LETZE CHATS",
    features: "FUNKTIONEN",
    featureBuildingCodes: "Österreichische Bauvorschriften",
    featureBuildingCodesDesc: "Zugriff auf umfassende Bauvorschriften",
    featureAreaCalculations: "Berechnungen",
    featureAreaCalculationsDesc: "Erhalte genaue Formeln und Anforderungen",
    featureLegalCitations: "Rechtszitate",
    featureLegalCitationsDesc: "Detaillierte Quellenangaben mit Seitenzahlen",
    featurePdfDocuments: "PDF-Dokumente",
    featurePdfDocumentsDesc: "Durchsuche originale österreichische Rechtsdokumente",
    askQuestionsPrompt: "Stellen Sie Fragen zu österreichischen Bauvorschriften, Spielplatzanforderungen, Bauvorschriften und mehr.",
    
    // MessageBubble
    you: "Sie",
    assistant: "Normo Assistent",
    sources: "Quellen",
    source: "Quelle",
    containsCalculations: "enthält Berechnungen",
    
    // CitationsList
    legalSourcesCitations: "Rechtliche Quellen & Zitate",
    page: "Seite",
    section: "Abschnitt",
    calculationsFound: "Berechnungen gefunden:",
    areaMeasurements: "Flächenmessungen:",
    allCitationsOfficial: "Alle Zitate stammen aus offiziellen österreichischen Rechtsdokumenten",
    
    // MetadataSidebar
    queryAnalysis: "Abfrageanalyse",
    extractedMetadata: "Erweiterte Metadaten zu deiner Rechtsanfrage",
    country: "Land",
    stateRegion: "Bundesland",
    legalDomain: "Rechtsgebiet",
    documentType: "Dokumenttyp",
    subjectArea: "Themengebiet",
    notSpecified: "Nicht angegeben",
    additionalFields: "Zusätzliche Felder",
    metadataHelpText: "Diese Metadaten helfen unserer KI, den rechtlichen Kontext deiner Anfrage zu verstehen und die relevantesten österreichischen Gesetze auszuwählen.",
    
    // General
    newConversation: "Neue Konversation",
    unknown: "Unbekannt",
    msgs: "msgs",
  },
};

export type TranslationKey = keyof typeof translations.de;

