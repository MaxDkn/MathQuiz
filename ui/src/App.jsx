import React, { useState, useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import "./index.css";

// ─────────────────────────────────────────────────────────────
// Constantes & Styles
// ─────────────────────────────────────────────────────────────

const API_URL = "http://localhost:8000";
const ENDPOINT_URL = `${API_URL}/api`;
const ALL_SUBJECTS = ["Algebra", "Arithmetic", "Geometry", "Trigonometry"];

const COLORS = [
  "var(--button-color-1)",
  "var(--button-color-2)",
  "var(--button-color-3)",
  "var(--button-color-4)"
];

const answerButtonStyle = {
  fontSize: "calc(1rem + 0.5vw)",
  whiteSpace: "normal",
  wordBreak: "normal"
};

const questionStyle = {
  fontSize: "calc(1rem + 1vw)"
};

// ─────────────────────────────────────────────────────────────
// Composant pour afficher le LaTeX avec KaTeX
// ─────────────────────────────────────────────────────────────

const MathComponent = ({ latex }) => {
  const mathRef = useRef(null);

  useEffect(() => {
    if (window.katex && mathRef.current) {
      window.katex.render(latex, mathRef.current, {
        throwOnError: false,
        strict: false,
      });
    }
  }, [latex]);

  return (
    <span ref={mathRef} style={{ whiteSpace: "nowrap", display: "inline-block" }} />
  );
};

// Transforme un texte contenant des portions LaTeX délimitées par $...$
const parseMathText = (text) => {
  if (typeof text !== "string") return text;
  const parts = text.split(/(\$[^$]+\$)/g);
  return parts.map((part, index) =>
    part.startsWith("$") && part.endsWith("$") ? (
      <MathComponent key={index} latex={part.slice(1, -1)} />
    ) : (
      part
    )
  );
};

// Function to shuffle an array (for colors)
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


// ─────────────────────────────────────────────────────────────
// Fonctions d'appel à l'API
// ─────────────────────────────────────────────────────────────

// Récupère une question depuis l'API
async function fetchQuestion(subjects) {
  const response = await fetch(`${ENDPOINT_URL}/generate`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ subjects, latex: true }),
  });

  if (!response.ok) {
    throw new Error("Erreur lors de la récupération de la question");
  }

  const data = await response.json();

  // Transformation : true/false deviennent "Oui"/"Non"
  const transformedAnswers = data.suggested_answer.map((answer) =>
    answer === true ? "Oui" : answer === false ? "Non" : answer
  );

  return { ...data, suggested_answer: transformedAnswers };
}

// Récupère le score final depuis l'API
async function getScore(metaData) {
  const response = await fetch(`${ENDPOINT_URL}/score`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(metaData),
  });

  if (!response.ok) {
    throw new Error("Erreur lors de la récupération du score");
  }
  return response.json();
}

// ─────────────────────────────────────────────────────────────
// Écran d'accueil avec sélection des sujets et paramètres
// ─────────────────────────────────────────────────────────────

const WelcomeScreen = ({
  subjects,
  handleSubjectChange,
  numQuestions,
  setNumQuestions,
  launchGame,
}) => {
  const [showSettings, setShowSettings] = useState(false);

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

  const handleBackgroundClick = () => {
    if (!showSettings && subjects.length > 0 && numQuestions >= 1) {
      launchGame();
    }
  };

  return (
    <div
      className="welcome-screen position-relative vh-100"
      onClick={handleBackgroundClick}
      style={{ cursor: !showSettings ? "pointer" : "default" }}
    >
      {/* Titre */}
      <div className="position-absolute top-0 start-50 translate-middle-x p-3">
        <h1 className="display-1">
          {parseMathText("$\\mathbb{M}ath\\mathbb{Q}ui^2z$")}
        </h1>
      </div>

      {/* Icône des paramètres */}
      <div className="position-absolute top-0 end-0 p-3">
        <div
          onClick={toggleSettings}
          style={{ cursor: "pointer" }}
          title="Paramètres"
        >
          <i className="bi bi-gear-fill fs-3"></i>
        </div>
      </div>

      {/* Carte des paramètres */}
      {showSettings && (
        <div
          className="card p-5 shadow-lg rounded-4 position-absolute top-50 start-50 translate-middle"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="mb-4">
            <h5>Sujets</h5>
            <div className="d-flex flex-wrap gap-3">
              {ALL_SUBJECTS.map((subject, index) => (
                <div key={index} className="form-check">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    id={`subject-${subject}`}
                    value={subject}
                    onChange={(e) => {
                      e.stopPropagation();
                      handleSubjectChange(e);
                    }}
                    checked={subjects.includes(subject)}
                  />
                  <label
                    className="form-check-label"
                    htmlFor={`subject-${subject}`}
                  >
                    {subject}
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

      {/* Texte clignotant pour lancer la partie */}
      {!showSettings && (
        <div className="position-absolute top-50 start-50 translate-middle">
          <div
            className="blinking-text"
            style={{ fontSize: "1.5rem", fontWeight: "bold" }}
          >
            Appuyer pour jouer
          </div>
        </div>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────────────────────
// Écran de score
// ─────────────────────────────────────────────────────────────

const ScoreScreen = ({ scoreMetaData, onWelcomeScreen, newSerie }) => {
  const { data: score, isLoading, isError } = useQuery({
    queryKey: ["score", scoreMetaData],
    queryFn: () => getScore(scoreMetaData),
    enabled: true,
  });

  if (isLoading) return <div>Chargement du score...</div>;
  if (isError) return <div>Erreur lors du chargement du score.</div>;

  return (
    <div className="text-center">
      <h1>Score : {score}</h1>
      <button className="btn btn-secondary m-2" onClick={onWelcomeScreen}>
        Retour à l'accueil
      </button>
      <button className="btn btn-primary m-2" onClick={newSerie}>
        Recommencer
      </button>
    </div>
  );
};

// ─────────────────────────────────────────────────────────────
// Composant principal : App
// ─────────────────────────────────────────────────────────────

function App() {
  // États de la partie
  const [gameStarted, setGameStarted] = useState(false);
  const [shuffledColors, setShuffledColors] = useState([]);
  const [showPopup, setShowPopup] = useState(false);
  const [popupMessage, setPopupMessage] = useState("");
  const [viewportHeight, setViewportHeight] = useState(window.innerHeight);
  const [subjects, setSubjects] = useState(ALL_SUBJECTS);
  const [numQuestions, setNumQuestions] = useState(15);
  const [currentQuestion, setCurrentQuestion] = useState(1);
  const [scoreMetaData, setScoreMetaData] = useState({ answers: {} });
  const [questionStartTime, setQuestionStartTime] = useState(Date.now());
  const [showScoreScreen, setShowScoreScreen] = useState(false);
  const [seriesId, setSeriesId] = useState(0);


  // Mise à jour de la hauteur de la fenêtre
  useEffect(() => {
    const updateHeight = () => setViewportHeight(window.innerHeight);
    window.addEventListener("resize", updateHeight);
    return () => window.removeEventListener("resize", updateHeight);
  }, []);

  // Récupération de la question via React Query
  const {
    data: questionData,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["generate", subjects, seriesId],
    queryFn: () => fetchQuestion(subjects),
    enabled: gameStarted,
  });
  

  // Mélange des couleurs dès qu'une nouvelle question est chargée
  useEffect(() => {
    if (questionData) {
      setShuffledColors(shuffleArray(COLORS));
    }
  }, [questionData]);

  // Gestion du changement de sujet
  const handleSubjectChange = (e) => {
    const subject = e.target.value;
    if (e.target.checked) {
      setSubjects((prev) => [...prev, subject]);
    } else {
      setSubjects((prev) => prev.filter((s) => s !== subject));
    }
  };

  // Lancer une nouvelle série de questions
  const launchSeries = () => {
    setSeriesId((prev) => prev + 1);
    setGameStarted(true);
    setShowScoreScreen(false);
    setScoreMetaData({ answers: {} });
    setCurrentQuestion(1);
    setQuestionStartTime(Date.now());
  };
  

  // Si le jeu n'est pas lancé, afficher l'écran d'accueil
  if (!gameStarted) {
    return (
      <WelcomeScreen
        subjects={subjects}
        handleSubjectChange={handleSubjectChange}
        numQuestions={numQuestions}
        setNumQuestions={setNumQuestions}
        launchGame={launchSeries}
      />
    );
  }

  // Si la série est terminée, afficher l'écran de score
  if (showScoreScreen) {
    return (
      <ScoreScreen
        scoreMetaData={scoreMetaData}
        onWelcomeScreen={() => setGameStarted(false)}
        newSerie={launchSeries}
      />
    );
  }

  // Afficher un spinner ou un message d'erreur en cas de problème
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
              zIndex: 10,
            }}
          >
            <div className="alert alert-danger" role="alert">
              Erreur lors de la récupération des données. Vérifiez l'API.
            </div>
          </div>
        )}
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            zIndex: 5,
          }}
        >
          <div className="spinner-border" role="status" />
        </div>
      </div>
    );
  }

  // Passage à la question suivante ou fin de la série
  const nextQuestion = () => {
    if (currentQuestion >= numQuestions) {
      setShowScoreScreen(true);
    } else {
      refetch();
      setCurrentQuestion((prev) => prev + 1);
      setQuestionStartTime(Date.now());
    }
  };

  // Vérifie la réponse sélectionnée
  const validAnswer = (selectedIndex) => {
    const timeTaken = (Date.now() - questionStartTime) / 1000;
    setScoreMetaData((prev) => ({
      ...prev,
      answers: {
        ...prev.answers,
        [currentQuestion]: {
          question_name: questionData.question_name,
          subject: questionData.subject,
          timeTaken,
          correct: selectedIndex === questionData.index_answer,
        },
      },
    }));

    if (selectedIndex !== questionData.index_answer) {
      setPopupMessage(
        <>
          Vous vous êtes trompé, la bonne réponse était{" "}
          {parseMathText(questionData.suggested_answer[questionData.index_answer])}
        </>
      );
      setShowPopup(true);
    } else {
      nextQuestion();
    }
  };

  // Ferme la popup d'erreur et passe à la suite
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
          ...questionStyle,
        }}
      >
        {parseMathText(questionData.question)}
      </div>

      <div className="answers d-flex flex-column" style={{ flex: 1, margin: "20px" }}>
        {questionData.suggested_answer.map((answer, index) => {
          if (index % 2 === 0) {
            return (
              <div className="row d-flex" style={{ flex: 1 }} key={index}>
                <div className="col p-2" style={{ flex: 1 }}>
                  <button
                    className="btn w-100 h-100"
                    onClick={() => validAnswer(index)}
                    style={{
                      backgroundColor: shuffledColors[index % shuffledColors.length],
                      color: "var(--question-text)",
                      ...answerButtonStyle,
                    }}
                  >
                    {parseMathText(answer)}
                  </button>
                </div>
                {questionData.suggested_answer[index + 1] && (
                  <div className="col p-2" style={{ flex: 1 }}>
                    <button
                      className="btn w-100 h-100"
                      onClick={() => validAnswer(index + 1)}
                      style={{
                        backgroundColor: shuffledColors[(index + 1) % shuffledColors.length],
                        color: "var(--question-text)",
                        ...answerButtonStyle,
                      }}
                    >
                      {parseMathText(questionData.suggested_answer[index + 1])}
                    </button>
                  </div>
                )}
              </div>
            );
          }
          return null;
        })}
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
            cursor: "pointer",
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
              width: "80%",
            }}
          >
            <h5 style={{ color: "red", marginBottom: "15px" }}>Erreur de Réponse</h5>
            <p>{popupMessage}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
