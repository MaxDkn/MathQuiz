import React, { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import "./index.css";

// URL and constants
const API_URL = "http://127.0.0.1:8000";
const ENDPOINT_URL = `${API_URL}/api`;
const all_subjects = ["Algebra", "Arithmetic", "Geometry", "Trigonometry"];

// Colors (using CSS variables)
const colors = [
  "var(--button-color-1)",
  "var(--button-color-2)",
  "var(--button-color-3)",
  "var(--button-color-4)"
];

// Responsive styles for the question and answers
const answerButtonStyle = {
  fontSize: "calc(1rem + 0.5vw)",
  whiteSpace: "normal",
  wordBreak: "normal"
};

const questionStyle = {
  fontSize: "calc(1rem + 1vw)"
};

// Component to display LaTeX with KaTeX
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

// Function to split text based on $...$ delimiters and render LaTeX
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

// Fetch data from the API (for questions and answers)
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

// Function to get the score from the API
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

// Welcome screen component with settings and subject selection
const WelcomeScreen = ({
  subjects,
  handleSubjectChange,
  numQuestions,
  setNumQuestions,
  launchGame
}) => {
  const [showSettings, setShowSettings] = useState(false);

  // Launch game with Enter key if settings are not shown
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

  // Clicking on the background launches the game if settings are not shown
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
        cursor: !showSettings ? "pointer" : "default"
      }}
    >
      {/* Title at the top center */}
      <div className="position-absolute top-0 start-50 translate-middle-x p-3">
        <h1 className="display-1">
          {parseMathText("$\\mathbb{M}ath\\mathbb{Q}ui^2z$")}
        </h1>
      </div>

      {/* Settings icon in the top right */}
      <div className="position-absolute top-0 end-0 p-3">
        <div onClick={toggleSettings} style={{ cursor: "pointer" }} title="Paramètres">
          <i className="bi bi-gear-fill fs-3"></i>
        </div>
      </div>

      {/* Settings card */}
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

      {/* Blinking text to prompt user to start */}
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

// Score screen component using React Query to fetch the score
const ScoreScreen = ({ scoreMetaData, onBack }) => {
  const { data: score, isLoading, isError } = useQuery(
    ["score", scoreMetaData],
    () => getScore(scoreMetaData),
    { enabled: true }
  );

  if (isLoading) {
    return <div>Loading score...</div>;
  }

  if (isError) {
    return <div>Error loading score.</div>;
  }

  return (
    <div>
      <h1>Score ! {score}</h1>
      <button onClick={onBack}>Back</button>
    </div>
  );
};

function App() {
  // Game state and configuration
  const [gameStarted, setGameStarted] = useState(false);
  const [shuffledColors, setShuffledColors] = useState([]);
  const [showPopup, setShowPopup] = useState(false);
  const [popupMessage, setPopupMessage] = useState("");
  const [viewportHeight, setViewportHeight] = useState(window.innerHeight);
  const [subjects, setSubjects] = useState(all_subjects);
  const [numQuestions, setNumQuestions] = useState(3);
  const [currentQuestion, setCurrentQuestion] = useState(1);
  const [scoreMetaData, setScoreMetaData] = useState({ answers: {} });
  const [questionStartTime, setQuestionStartTime] = useState(Date.now());
  const [showScoreScreen, setShowScore] = useState(false);

  // Update viewport height on resize (useful for mobile devices)
  useEffect(() => {
    const updateHeight = () => setViewportHeight(window.innerHeight);
    window.addEventListener("resize", updateHeight);
    return () => window.removeEventListener("resize", updateHeight);
  }, []);

  // Fetch question data after the game starts
  const { data, isError, isLoading, refetch } = useQuery(
    ["generate"],
    () => fetchData(subjects),
    {
      enabled: gameStarted
    }
  );

  useEffect(() => {
    setShuffledColors(shuffleArray(colors));
  }, [data]);

  // Handle subject checkbox changes
  const handleSubjectChange = (e) => {
    const subject = e.target.value;
    if (e.target.checked) {
      setSubjects((prev) => [...prev, subject]);
    } else {
      setSubjects((prev) => prev.filter((s) => s !== subject));
    }
  };

  // Start a new game series
  const launchSeries = () => {
    setGameStarted(true);
    setShowScore(false);
    setScoreMetaData({ answers: {} });
    setCurrentQuestion(1);
  };

  // Show the welcome screen until the game starts
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

  // Render the score screen when the game is over
  if (showScoreScreen) {
    return (
      <ScoreScreen
        scoreMetaData={scoreMetaData}
        onBack={() => launchSeries()}
      />
    );
  }

  // Show a spinner or error message if data is loading or there is an error
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
      </div>
    );
  }

  // Move to the next question or show the score screen when finished
  const nextQuestion = () => {
    if (currentQuestion >= numQuestions) {
      console.log(scoreMetaData);
      setShowScore(true);
    } else {
      refetch();
      setCurrentQuestion(currentQuestion + 1);
      setQuestionStartTime(Date.now());
    }
  };

  // Validate the selected answer
  function validAnswer(index) {
    const timeTaken = (Date.now() - questionStartTime) / 1000;
    setScoreMetaData((prev) => ({
      ...prev,
      answers: {
        ...prev.answers,
        [`${currentQuestion}`]: {
          question_name: data.question_name,
          subject: data.subject,
          timeTaken: timeTaken,
          correct_answer: index === data.index_answer,
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
    }
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
