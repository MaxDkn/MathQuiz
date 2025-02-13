import React, { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import "./index.css";

// URL et constantes
const API_URL = "http://127.0.0.1:8000";
const ENDPOINT_URL = `${API_URL}/api`;
const all_subjects = ["Algebra", "Arithmetic", "Geometry", "Trigonometry"];

// Remplacer les couleurs en dur par des références aux variables CSS
const colors = [
  "var(--button-color-1)",
  "var(--button-color-2)",
  "var(--button-color-3)",
  "var(--button-color-4)"
];

// Styles responsive pour la question et les réponses
const answerButtonStyle = {
  fontSize: "calc(1rem + 0.5vw)",
  whiteSpace: "normal",
  wordBreak: "normal"
};

const questionStyle = {
  fontSize: "calc(1rem + 1vw)"
};

// Composant pour afficher le LaTeX avec KaTeX
const MathComponent = ({ latex }) => {
  const mathRef = React.useRef(null);

  useEffect(() => {
    if (window.katex && mathRef.current) {
      window.katex.render(latex, mathRef.current, {
        throwOnError: false,
        strict: false
      });
    }
  }, [latex]);

  return (
    <span
      ref={mathRef}
      style={{ whiteSpace: "nowrap", display: "inline-block" }}
    ></span>
  );
};

// Fonction qui découpe le texte sur les délimiteurs $...$
const parseMathText = (text) => {
  if (typeof text !== "string") {
    return text;
  }

  const parts = text.split(/(\$[^$]+\$)/g);
  return parts.map((part, index) => {
    if (part.startsWith("$") && part.endsWith("$")) {
      const latex = part.slice(1, -1);
      return <MathComponent key={index} latex={latex} />;
    }
    return part;
  });
};

// Fonction pour mélanger un tableau (ici pour les couleurs)
const shuffleArray = (array) => {
  let shuffledArray = [...array];
  for (let i = shuffledArray.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffledArray[i], shuffledArray[j]] = [
      shuffledArray[j],
      shuffledArray[i]
    ];
  }
  return shuffledArray;
};

// Récupération des données depuis l'API
async function fetchData(subjects_chosen) {
  const response = await fetch(`${ENDPOINT_URL}/generate`, {
    body: JSON.stringify({ subjects: subjects_chosen, latex: true }),
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json"
    },
    method: "POST"
  });

  if (!response.ok) {
    throw new Error("Network response was not ok");
  }
  const data = await response.json();

  const transformedAnswers = data.suggested_answer.map((answer) => {
    return answer === true ? "Oui" : answer === false ? "Non" : answer;
  });

  return { ...data, suggested_answer: transformedAnswers };
}

async function getScore(metaData) {
  const response = await fetch(`${ENDPOINT_URL}/score`, {
    body: JSON.stringify({ metaData }),
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json"
    },
    method: "POST"
  });

  if (!response.ok) {
    throw new Error("Network response was not ok");
  }
  const data = await response.json();
  return data;
}

const WelcomeScreen = ({
  subjects,
  handleSubjectChange,
  numQuestions,
  setNumQuestions,
  launchGame
}) => {
  const [showSettings, setShowSettings] = useState(false);

  // Lancer le jeu avec la touche "Entrée" uniquement si les réglages ne sont pas affichés
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (
        e.key === "Enter" &&
        subjects.length > 0 &&
        numQuestions >= 1 &&
        !showSettings
      ) {
        launchGame();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [subjects, numQuestions, launchGame, showSettings]);

  const toggleSettings = (e) => {
    e.stopPropagation();
    setShowSettings((prev) => !prev);
  };

  // Le clic sur le fond déclenche le lancement du jeu si les réglages ne sont pas affichés
  const handleBackgroundClick = () => {
    if (!showSettings && subjects.length > 0 && numQuestions >= 1) {
      launchGame();
    }
  };

  return (
    <div
      className="welcome-screen position-relative vh-100"
      onClick={handleBackgroundClick}
      style={{
        backgroundColor: colors[0],
        cursor: !showSettings ? "pointer" : "default"
      }}
    >
      {/* Titre en haut, centré */}
      <div className="position-absolute top-0 start-50 translate-middle-x p-3">
        <h1 className="display-1" style={{ color: colors[2] }}>{parseMathText("$\\mathbb{M}ath\\mathbb{Q}ui^2z$")}</h1>
      </div>

      {/* Icône des réglages en haut à droite */}
      <div className="position-absolute top-0 end-0 p-3">
        <div onClick={toggleSettings} style={{ cursor: "pointer", color: colors[3] }} title="Paramètres">
          <i className="bi bi-gear-fill fs-3"></i>
        </div>
      </div>

      {/* Card de réglages (affichée uniquement si activée) */}
      {showSettings && (
        <div
          className="card p-5 shadow-lg rounded-4 position-absolute top-50 start-50 translate-middle"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="mb-4">
            <h5>Sujets</h5>
            <div className="d-flex flex-wrap gap-3">
              {all_subjects.map((item, index) => (
                <div key={index} className="form-check">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    id={`subject-${item}`}
                    value={item}
                    onChange={(e) => {
                      e.stopPropagation();
                      handleSubjectChange(e);
                    }}
                    checked={subjects.includes(item)}
                  />
                  <label className="form-check-label" htmlFor={`subject-${item}`}>
                    {item}
                  </label>
                </div>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <h5>Nombre de questions</h5>
            <input
              type="number"
              id="numQuestions"
              className="form-control"
              min="1"
              value={numQuestions}
              onChange={(e) => {
                e.stopPropagation();
                setNumQuestions(Number(e.target.value));
              }}
            />
          </div>

          <button
            className="btn btn-primary w-100"
            onClick={(e) => {
              e.stopPropagation();
              launchGame();
            }}
            disabled={subjects.length === 0 || numQuestions < 1}
          >
            Jouer
          </button>
        </div>
      )}

      {/* Texte clignotant au centre si les réglages ne sont pas affichés */}
      {!showSettings && (
        <div className="position-absolute top-50 start-50 translate-middle">
          <div
            className="blinking-text"
            style={{ fontSize: "1.5rem", fontWeight: "bold", color: colors[2] }}
          >
            Appuyer pour jouer
          </div>
        </div>
      )}
    </div>
  );
};

const ScoreScreen = (scoreMetaData) => {
  return (
    <div>
      <h1>Score ! {getScore(scoreMetaData)}</h1>
    </div>
  )
}


function App() {
  // États pour le jeu, la sélection des sujets, etc.
  const [gameStarted, setGameStarted] = useState(false);
  const [shuffledColors, setShuffledColors] = useState([]);
  const [showPopup, setShowPopup] = useState(false);
  const [popupMessage, setPopupMessage] = useState("");
  const [viewportHeight, setViewportHeight] = useState(window.innerHeight);
  const [subjects, setSubjects] = useState(all_subjects);
  const [numQuestions, setNumQuestions] = useState(3);
  const [currentQuestion, setCurrentQuestion] = useState(1);
  const [scoreMetaData, setScoreMetaData] = useState({answers: {}});
  const [questionStartTime, setQuestionStartTime] = useState(Date.now());

  // Met à jour la hauteur de la fenêtre (utile sur iOS lorsque la barre d’outils disparaît)
  useEffect(() => {
    const updateHeight = () => setViewportHeight(window.innerHeight);
    window.addEventListener("resize", updateHeight);
    return () => window.removeEventListener("resize", updateHeight);
  }, []);

  // La requête s'exécute uniquement après le démarrage du jeu
  const { data, isError, isLoading, refetch } = useQuery(
    ["generate"],
    () => fetchData(subjects),
    {
      enabled: gameStarted // lancement uniquement après démarrage
    }
  );

  useEffect(() => {
    setShuffledColors(shuffleArray(colors));
  }, [data]);

  // Met à jour la sélection des sujets via les cases à cocher
  const handleSubjectChange = (e) => {
    const subject = e.target.value;
    if (e.target.checked) {
      setSubjects((prev) => [...prev, subject]);
    } else {
      setSubjects((prev) => prev.filter((s) => s !== subject));
    }
  };

  const launchSeries = () => {
    setGameStarted(true);
    setScoreMetaData({answers: {}})
    setCurrentQuestion(1)
  };

  // Écran d'accueil
  if (!gameStarted) {
    return <WelcomeScreen subjects={subjects}
                          handleSubjectChange={handleSubjectChange}
                          numQuestions={numQuestions}
                          setNumQuestions={setNumQuestions}
                          launchGame={launchSeries}/>
  }

  // Affichage du spinner ou du message d'erreur lors du chargement / en cas d'erreur
  if (isLoading || isError) {
    return (
      <div style={{ position: "relative", height: viewportHeight, width: "100vw" }}>
      {isError && (
        <div
          style={{
            position: "absolute",
            top: "10px",
            width: "100%",
            textAlign: "center",
            padding: "0 10px",
            zIndex: 10
          }}
        >
          <div className="alert alert-danger" role="alert">
            Erreur dans la récupération des données, l'API n'est pas connectée au frontend.
          </div>
        </div>
      )}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          zIndex: 5
        }}
      >
        <div className="spinner-border" role="status" />
      </div>
    </div>)
  }
  
  const nextQuestion = () => {
    if (currentQuestion >= numQuestions) {
      console.log(scoreMetaData)
      setGameStarted(false);
    }
    refetch();
    setCurrentQuestion(currentQuestion+1);
    setQuestionStartTime(Date.now())
  }

  // Fonction pour valider la réponse
  function validAnswer(index) {    
    const timeTaken = (Date.now() - questionStartTime) / 1000;
    // mise à jour des metadonnées
    setScoreMetaData(prev => ({
      ...prev,
      answers : {
        ...prev.answers,
         [currentQuestion] : {
          question_name: data.question_name,
          subject: data.subject,
          timeTaken: timeTaken,
          valid: true ? index === data.index_answer : false,
         }
      }
    }));

    if (index !== data.index_answer) {
      setPopupMessage(
        <>
          Vous vous êtes trompé, la bonne réponse était{" "}
          {parseMathText(data.suggested_answer[data.index_answer])}
        </>
      );
      setShowPopup(true);
    } else {
      nextQuestion();
    };
    
  }

  const closePopup = () => {
    setShowPopup(false);
    nextQuestion();
  };

  return (
    <div
      className="App container"
      style={{ display: "flex", flexDirection: "column", minHeight: viewportHeight }}
    >
      <div
        className="question text-center"
        style={{
          border: "2px solid var(--question-border)",
          padding: "10px",
          margin: "10px",
          fontWeight: "bold",
          backgroundColor: "var(--question-bg)",
          color: "var(--question-text)",
          ...questionStyle
        }}
      >
        {parseMathText(data.question)}
      </div>

      <div className="answers d-flex flex-column" style={{ flex: 1, margin: "20px" }}>
        {data.suggested_answer.map((item, index) =>
          index % 2 === 0 ? (
            <div className="row d-flex" style={{ flex: 1 }} key={index}>
              <div className="col p-2" style={{ flex: 1 }}>
                <button
                  className="btn w-100 h-100"
                  onClick={() => validAnswer(index)}
                  style={{
                    backgroundColor: shuffledColors[index % shuffledColors.length],
                    color: "var(--question-text)",
                    ...answerButtonStyle
                  }}
                >
                  {parseMathText(item)}
                </button>
              </div>
              {data.suggested_answer[index + 1] && (
                <div className="col p-2" style={{ flex: 1 }}>
                  <button
                    className="btn w-100 h-100"
                    onClick={() => validAnswer(index + 1)}
                    style={{
                      backgroundColor: shuffledColors[(index + 1) % shuffledColors.length],
                      color: "var(--question-text)",
                      ...answerButtonStyle
                    }}
                  >
                    {parseMathText(data.suggested_answer[index + 1])}
                  </button>
                </div>
              )}
            </div>
          ) : null
        )}
      </div>

      {showPopup && (
        <div
          onClick={closePopup}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100vw",
            height: viewportHeight,
            backgroundColor: "rgba(142, 22, 22, 0.6)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 1050,
            cursor: "pointer"
          }}
        >
          <div
            style={{
              backgroundColor: "var(--popup-bg)",
              color: "var(--popup-text)",
              padding: "20px",
              borderRadius: "10px",
              textAlign: "center",
              boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
              maxWidth: "500px",
              width: "80%"
            }}
          >
            <h5 style={{ color: "red", marginBottom: "15px" }}>
              Erreur de Réponse
            </h5>
            <p>{popupMessage}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
