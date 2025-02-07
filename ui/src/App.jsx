import React, { useState, useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";

// URL et constantes
const API_URL = "/api";
const ENDPOINT_URL = `${API_URL}/generate`;
const subjects = ["Arithmetic", "Algebra", "Trigonometry", "Geometry"];
const colors = ["#CEE5D0", "#F3F0D7", "#FED2AA", "#F0C1E1"];

// Styles responsive pour la question et les réponses
const answerButtonStyle = {
  fontSize: "calc(1rem + 0.5vw)", // taille responsive pour les réponses
  whiteSpace: "normal",           // permet le retour à la ligne s'il y a des espaces
  wordBreak: "normal",            // casse les mots uniquement en présence d'espaces (par défaut)
  // Vous pouvez ajouter textAlign ou d'autres styles si nécessaire
};


const questionStyle = {
  fontSize: "calc(1rem + 1vw)",    // taille responsive plus grande pour la question
};

// Composant pour afficher le LaTeX avec KaTeX
const MathComponent = ({ latex }) => {
  const mathRef = useRef(null);

  useEffect(() => {
    if (window.katex && mathRef.current) {
      window.katex.render(latex, mathRef.current, {
        throwOnError: false,
      });
    }
  }, [latex]);

  return <span ref={mathRef}></span>;
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
    [shuffledArray[i], shuffledArray[j]] = [shuffledArray[j], shuffledArray[i]];
  }
  return shuffledArray;
};

// Récupération des données depuis l'API
async function fetchData() {
  const response = await fetch(ENDPOINT_URL, {
    body: JSON.stringify({ subjects }),
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    method: "POST",
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

function App() {
  const { data, isError, isLoading, refetch } = useQuery(["generate"], fetchData);
  const [shuffledColors, setShuffledColors] = useState([]);
  const [showPopup, setShowPopup] = useState(false);
  const [popupMessage, setPopupMessage] = useState("");

  function validAnswer(index) {
    if (index !== data.index_answer) {
      setPopupMessage(
          <>
            Vous vous êtes trompé, la bonne réponse était{" "}
            {parseMathText(data.suggested_answer[data.index_answer])}
          </>
      );
      setShowPopup(true);
    } else {
      refetch();
    }
  }

  const closePopup = () => {
    setShowPopup(false);
    refetch();
  };

  useEffect(() => {
    setShuffledColors(shuffleArray(colors));
  }, [data]);

  if (isLoading || isError) {
    return (
        <div style={{ position: "relative", height: "100vh", width: "100vw" }}>
          {isError && (
              <div
                  style={{
                    position: "absolute",
                    top: "10px", // Le message est placé en haut (par exemple à 20% de la hauteur)
                    width: "100%",
                    textAlign: "center",
                    padding: "0 10px",
                    zIndex: 10,
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
                zIndex: 5,
              }}
          >
            <div className="spinner-border" role="status" />
          </div>
        </div>
    );
  }

  return (
      // Conteneur principal en flex-column occupant toute la hauteur de la fenêtre
      <div className="App container" style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
        {/* Zone de la question */}
        <div
            className="question text-center"
            style={{
              border: "2px solid black",
              padding: "10px",
              margin: "10px",
              fontWeight: "bold",
              backgroundColor: "#f9f9f9",
              ...questionStyle,
            }}
        >
          {parseMathText(data.question)}
        </div>

        {/* Zone des réponses qui prend l'espace restant */}
        <div className="answers d-flex flex-column" style={{ flex: 1, margin: "20px" }}>
          {data.suggested_answer.map((item, index) =>
              index % 2 === 0 ? (
                  // Chaque ligne (row) partage équitablement la hauteur
                  <div className="row d-flex" style={{ flex: 1 }} key={index}>
                    <div className="col p-2" style={{ flex: 1 }}>
                      <button
                          className="btn w-100 h-100"
                          onClick={() => validAnswer(index)}
                          style={{
                            backgroundColor: shuffledColors[index % shuffledColors.length],
                            ...answerButtonStyle,
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
                                ...answerButtonStyle,
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

        {/* Modal Popup */}
        {showPopup && (
            <div
                onClick={closePopup}
                style={{
                  position: "fixed",
                  top: 0,
                  left: 0,
                  width: "100vw",
                  height: "100vh",
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
                    backgroundColor: "white",
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