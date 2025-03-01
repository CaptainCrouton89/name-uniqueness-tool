import axios from "axios";
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Title,
  Tooltip,
} from "chart.js";
import React, { useState } from "react";
import { Bar, Doughnut } from "react-chartjs-2";

// Create custom axios instance with base URL
const api = axios.create({
  baseURL: "http://localhost:5001/api",
});

// Register ChartJS components
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title
);

// Define TypeScript interfaces
interface NameScore {
  firstName?: string;
  lastName?: string;
  fullName?: string;
  score: number;
  type: "first" | "last" | "full";
}

interface ComparisonResult {
  name: string;
  score: number;
}

interface ComparisonResponse {
  results: ComparisonResult[];
}

const App: React.FC = () => {
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [result, setResult] = useState<NameScore | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [comparisonNames, setComparisonNames] = useState<string>("");
  const [comparisonResults, setComparisonResults] = useState<
    ComparisonResult[]
  >([]);
  const [activeTab, setActiveTab] = useState<"single" | "compare">("single");

  const handleScoreName = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!firstName && !lastName) {
      setError("Please enter at least one name");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.post("/score-name", {
        firstName,
        lastName,
      });

      setResult(response.data);
    } catch (err) {
      setError("An error occurred while scoring the name. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCompareNames = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!comparisonNames.trim()) {
      setError("Please enter names to compare");
      return;
    }

    // Parse the names from the textarea
    const namesList = comparisonNames
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0)
      .map((line) => {
        const parts = line.split(" ");
        if (parts.length === 1) {
          return [parts[0], ""];
        }
        const lastName = parts.slice(1).join(" ");
        return [parts[0], lastName];
      });

    if (namesList.length === 0) {
      setError("Please enter at least one name to compare");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.post<ComparisonResponse>("/compare-names", {
        names: namesList,
      });

      setComparisonResults(response.data.results);
    } catch (err) {
      setError("An error occurred while comparing names. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Prepare chart data for single name score
  const scoreChartData = {
    labels: ["Uniqueness Score", "Remaining"],
    datasets: [
      {
        data: result ? [result.score, 100 - result.score] : [0, 100],
        backgroundColor: ["#0080ff", "#e2e8f0"],
        borderWidth: 0,
      },
    ],
  };

  // Prepare chart data for name comparison
  const comparisonChartData = {
    labels: comparisonResults.map((item) => item.name),
    datasets: [
      {
        label: "Uniqueness Score",
        data: comparisonResults.map((item) => item.score),
        backgroundColor: "#0080ff",
      },
    ],
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-primary py-6 shadow-md">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold text-white">
            Name Uniqueness Dashboard
          </h1>
          <p className="text-blue-100 mt-2">
            Analyze and compare the uniqueness of names based on frequency,
            structure, and letter distribution
          </p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="flex border-b">
            <button
              className={`px-6 py-3 font-medium text-sm focus:outline-none ${
                activeTab === "single"
                  ? "bg-primary text-white"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
              onClick={() => setActiveTab("single")}
            >
              Score a Name
            </button>
            <button
              className={`px-6 py-3 font-medium text-sm focus:outline-none ${
                activeTab === "compare"
                  ? "bg-primary text-white"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
              onClick={() => setActiveTab("compare")}
            >
              Compare Names
            </button>
          </div>

          <div className="p-6">
            {activeTab === "single" ? (
              <div>
                <form onSubmit={handleScoreName} className="mb-8">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <label
                        htmlFor="firstName"
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        First Name
                      </label>
                      <input
                        type="text"
                        id="firstName"
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                        placeholder="Enter first name"
                      />
                    </div>
                    <div>
                      <label
                        htmlFor="lastName"
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Last Name
                      </label>
                      <input
                        type="text"
                        id="lastName"
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                        placeholder="Enter last name"
                      />
                    </div>
                  </div>
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full md:w-auto px-6 py-2 bg-primary hover:bg-primary-dark text-white font-medium rounded-md shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                  >
                    {loading ? "Calculating..." : "Calculate Uniqueness Score"}
                  </button>
                </form>

                {error && (
                  <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
                    <p className="text-red-700">{error}</p>
                  </div>
                )}

                {result && (
                  <div className="bg-secondary p-6 rounded-lg">
                    <h2 className="text-2xl font-bold text-gray-800 mb-4">
                      {result.type === "full"
                        ? result.fullName
                        : result.type === "first"
                        ? result.firstName
                        : result.lastName}
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      <div>
                        <div className="mb-4">
                          <h3 className="text-lg font-medium text-gray-700 mb-2">
                            Uniqueness Score
                          </h3>
                          <div className="text-5xl font-bold text-primary">
                            {result.score}/100
                          </div>
                        </div>

                        <div className="mt-6">
                          <h3 className="text-lg font-medium text-gray-700 mb-2">
                            Interpretation
                          </h3>
                          <p className="text-gray-600">
                            {result.score >= 90
                              ? "Extremely unique name, very rarely encountered."
                              : result.score >= 75
                              ? "Highly unique name, stands out significantly."
                              : result.score >= 60
                              ? "Very unique name, quite distinctive."
                              : result.score >= 45
                              ? "Moderately unique name, somewhat distinctive."
                              : result.score >= 30
                              ? "Slightly unique name, a bit uncommon."
                              : "Common name, frequently encountered."}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center justify-center">
                        <div className="w-48 h-48">
                          <Doughnut
                            data={scoreChartData}
                            options={{
                              cutout: "75%",
                              plugins: {
                                legend: {
                                  display: false,
                                },
                                tooltip: {
                                  enabled: false,
                                },
                              },
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div>
                <form onSubmit={handleCompareNames} className="mb-8">
                  <div className="mb-4">
                    <label
                      htmlFor="comparisonNames"
                      className="block text-sm font-medium text-gray-700 mb-1"
                    >
                      Names to Compare (one per line)
                    </label>
                    <textarea
                      id="comparisonNames"
                      value={comparisonNames}
                      onChange={(e) => setComparisonNames(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                      placeholder="Enter names to compare (one per line)"
                      rows={5}
                    />
                    <p className="mt-1 text-sm text-gray-500">
                      Example: John Smith
                      <br />
                      Luna Zhang
                      <br />
                      Zephyr
                    </p>
                  </div>
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full md:w-auto px-6 py-2 bg-primary hover:bg-primary-dark text-white font-medium rounded-md shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                  >
                    {loading ? "Comparing..." : "Compare Names"}
                  </button>
                </form>

                {error && (
                  <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
                    <p className="text-red-700">{error}</p>
                  </div>
                )}

                {comparisonResults.length > 0 && (
                  <div className="bg-secondary p-6 rounded-lg">
                    <h2 className="text-2xl font-bold text-gray-800 mb-6">
                      Name Comparison Results
                    </h2>

                    <div className="mb-8">
                      <Bar
                        data={comparisonChartData}
                        options={{
                          indexAxis: "y",
                          scales: {
                            x: {
                              beginAtZero: true,
                              max: 100,
                              title: {
                                display: true,
                                text: "Uniqueness Score",
                              },
                            },
                          },
                          plugins: {
                            legend: {
                              display: false,
                            },
                          },
                        }}
                      />
                    </div>

                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th
                              scope="col"
                              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                              Rank
                            </th>
                            <th
                              scope="col"
                              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                              Name
                            </th>
                            <th
                              scope="col"
                              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                              Uniqueness Score
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {comparisonResults
                            .sort((a, b) => b.score - a.score)
                            .map((result, index) => (
                              <tr key={index}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                  {index + 1}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                  {result.name}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                  {result.score}/100
                                </td>
                              </tr>
                            ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      <footer className="bg-gray-800 text-white py-6">
        <div className="container mx-auto px-4">
          <p className="text-center text-gray-400">
            Name Uniqueness Dashboard &copy; {new Date().getFullYear()}
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;
