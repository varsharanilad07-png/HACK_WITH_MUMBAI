import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Copy, Download, FileText, ShieldCheck, UploadCloud } from "lucide-react";
import Panel from "../../components/ui/Panel";
import { resumeApi } from "../../lib/api";
import { getAnalysisResult, saveAnalysisResult } from "../../lib/analysisStorage";

const MIN_RESUME_SIZE_KB = 50;
const MAX_RESUME_SIZE_MB = 10;
const BYTES_PER_KB = 1024;
const BYTES_PER_MB = 1024 * 1024;

function formatFileSize(bytes) {
  return `${(bytes / BYTES_PER_MB).toFixed(2)} MB`;
}

export default function ResumeUploadPage() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileError, setFileError] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [resumeError, setResumeError] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedResume, setGeneratedResume] = useState("");
  const [resumeForm, setResumeForm] = useState({
    name: "Varsharani Lad",
    phone: "9284073325",
    email: "varsharanilad7@gmail.com",
    linkedin: "linkedin.com/in/varsharani-lad-105592306/",
    github: "github.com/Varsha7781",
    education: "MIT Academy Of Engineering, CGPA - 8.46; Sanjay Ghodawat Junior College, HSC - 75.00",
    current_role: "Networking Intern",
    skills: "Python, Computer Networking, Network Automation, Network Topology, Cisco Packet Tracer",
    experience: "Cisco (June-August 2025): Completed intensive technical modules covering advanced computer networking concepts, routing protocols, switching, and network security architectures. Designed and developed an automated network topology generator that dynamically provisions and configures network infrastructures based on user-defined parameters.",
    projects: "SAKHI – Your Virtual PCOD Health Assistant: AI-driven healthcare platform with ensemble ML and a knowledge graph conversational agent. | EDUSYNC – AI-powered career path recommender system: FastAPI, ReactJS, MongoDB, AWS, and Groq APIs.",
    achievements: "Resolved 150+ LeetCode challenges with focus on dynamic programming, string, graph, and array problems.",
    interests: "AI, networking, machine learning, healthcare technology, career guidance",
  });

  useEffect(() => {
    const analysis = getAnalysisResult();
    if (!analysis?.parsed_profile) {
      return;
    }

    const profile = analysis.parsed_profile;
    setResumeForm((current) => ({
      ...current,
      name: profile.name || current.name,
      skills: Array.isArray(profile.skills) ? profile.skills.join(", ") : current.skills,
      education: profile.education || current.education,
      current_role: profile.current_role || current.current_role,
      interests: Array.isArray(profile.interests) ? profile.interests.join(", ") : current.interests,
      phone: profile.phone || current.phone,
      email: profile.email || current.email,
      linkedin: profile.linkedin || current.linkedin,
      github: profile.github || current.github,
      experience: Array.isArray(profile.experience) ? profile.experience.join(" ") : current.experience,
      projects: Array.isArray(profile.projects) ? profile.projects.join(" | ") : current.projects,
      achievements: Array.isArray(profile.achievements) ? profile.achievements.join(" | ") : current.achievements,
    }));
  }, []);

  function handleResumeChange(event) {
    const file = event.target.files?.[0];
    setSelectedFile(null);
    setFileError("");

    if (!file) {
      return;
    }

    const fileSizeMb = file.size / BYTES_PER_MB;
    const fileSizeKb = file.size / BYTES_PER_KB;

    if (fileSizeKb < MIN_RESUME_SIZE_KB || fileSizeMb > MAX_RESUME_SIZE_MB) {
      setFileError(`Resume must be between ${MIN_RESUME_SIZE_KB} KB and ${MAX_RESUME_SIZE_MB} MB. Selected file is ${formatFileSize(file.size)}.`);
      event.target.value = "";
      return;
    }

    setSelectedFile(file);
  }

  async function handleUpload() {
    if (!selectedFile) {
      setFileError(`Choose a valid PDF resume between ${MIN_RESUME_SIZE_KB} KB and ${MAX_RESUME_SIZE_MB} MB first.`);
      return;
    }

    setFileError("");
    setIsUploading(true);

    try {
      const { data } = await resumeApi.upload(selectedFile);
      saveAnalysisResult(data);
      navigate("/skills");
    } catch (error) {
      setFileError(error?.response?.data?.detail ?? "Resume parsing failed. Please try another PDF.");
    } finally {
      setIsUploading(false);
    }
  }

  function updateField(field, value) {
    setResumeForm((current) => ({ ...current, [field]: value }));
  }

  function buildResumePayload() {
    return {
      ...resumeForm,
      skills: resumeForm.skills
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      interests: resumeForm.interests
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      experience: resumeForm.experience
        .split("\n")
        .map((item) => item.trim())
        .filter(Boolean),
      projects: resumeForm.projects
        .split("|")
        .map((item) => item.trim())
        .filter(Boolean),
      achievements: resumeForm.achievements
        .split("|")
        .map((item) => item.trim())
        .filter(Boolean),
    };
  }

  async function handleGenerateResume() {
    setResumeError("");
    setIsGenerating(true);

    try {
      const payload = buildResumePayload();
      const { data } = await resumeApi.generate(payload);
      setGeneratedResume(data.resume ?? "");
      saveAnalysisResult({ ...(getAnalysisResult() || {}), generated_resume: data.resume, generated_profile: data.profile });
    } catch (error) {
      setResumeError(error?.response?.data?.detail ?? "Resume generation failed. Please check the input fields.");
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleDownloadWord() {
    setResumeError("");
    setIsGenerating(true);

    try {
      const payload = buildResumePayload();
      const response = await resumeApi.generateWord(payload);
      const blob = new Blob([response.data], {
        type: response.headers["content-type"] || "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      });
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "generated_resume.docx";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setResumeError(error?.response?.data?.detail ?? "Word download failed. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <Panel title="Upload Resume">
        <label className="focus-within:outline-accent flex min-h-80 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-accent/40 bg-accent/5 px-6 text-center transition hover:border-accent hover:bg-accent/10">
          <span className="grid h-16 w-16 place-items-center rounded-lg border border-accent/30 bg-accent/10">
            <UploadCloud className="text-accent" size={34} />
          </span>
          <span className="mt-4 text-lg font-semibold text-white">Drop resume or browse files</span>
          <span className="mt-2 max-w-md text-sm text-slate-400">Supports PDF files. File size must be between 50 KB and 10 MB.</span>
          <input className="sr-only" type="file" accept=".pdf" onChange={handleResumeChange} />
        </label>
        {fileError && (
          <p className="mt-4 rounded-lg border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-red-200">
            {fileError}
          </p>
        )}
        {selectedFile && (
          <>
            <div className="mt-4 flex items-center gap-3 rounded-lg border border-accent/40 bg-accent/10 px-4 py-3 text-sm text-teal-100">
              <ShieldCheck size={18} />
              <span>Selected {selectedFile.name} ({formatFileSize(selectedFile.size)})</span>
            </div>
            <button
              className="focus-ring mt-4 w-full rounded-lg bg-accent px-4 py-3 text-sm font-semibold text-slate-950 disabled:cursor-not-allowed disabled:opacity-60"
              onClick={handleUpload}
              disabled={isUploading}
            >
              {isUploading ? "Uploading and parsing..." : "Analyze Resume"}
            </button>
          </>
        )}
      </Panel>

      <Panel title="Generate Resume">
        <p className="text-sm text-slate-400">
          Fill in the fields below to generate a resume in the professional format you asked for.
        </p>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {[
            ["name", "Name"],
            ["phone", "Phone"],
            ["email", "Email"],
            ["linkedin", "LinkedIn"],
            ["github", "GitHub"],
            ["current_role", "Current Role"],
            ["education", "Education"],
          ].map(([field, label]) => (
            <label key={field} className="grid gap-2 text-sm text-slate-300 md:col-span-1">
              <span>{label}</span>
              <input
                className="rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-accent"
                value={resumeForm[field]}
                onChange={(event) => updateField(field, event.target.value)}
                placeholder={label}
              />
            </label>
          ))}

          <label className="grid gap-2 text-sm text-slate-300 md:col-span-2">
            <span>Skills (comma separated)</span>
            <textarea
              className="min-h-24 rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-accent"
              value={resumeForm.skills}
              onChange={(event) => updateField("skills", event.target.value)}
            />
          </label>

          <label className="grid gap-2 text-sm text-slate-300 md:col-span-2">
            <span>Experience</span>
            <textarea
              className="min-h-28 rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-accent"
              value={resumeForm.experience}
              onChange={(event) => updateField("experience", event.target.value)}
            />
          </label>

          <label className="grid gap-2 text-sm text-slate-300 md:col-span-2">
            <span>Projects</span>
            <textarea
              className="min-h-28 rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-accent"
              value={resumeForm.projects}
              onChange={(event) => updateField("projects", event.target.value)}
            />
          </label>

          <label className="grid gap-2 text-sm text-slate-300 md:col-span-2">
            <span>Achievements</span>
            <textarea
              className="min-h-24 rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-accent"
              value={resumeForm.achievements}
              onChange={(event) => updateField("achievements", event.target.value)}
            />
          </label>

          <label className="grid gap-2 text-sm text-slate-300 md:col-span-2">
            <span>Interests</span>
            <input
              className="rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-accent"
              value={resumeForm.interests}
              onChange={(event) => updateField("interests", event.target.value)}
            />
          </label>
        </div>

        <button
          className="focus-ring mt-4 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-accent px-4 py-3 text-sm font-semibold text-slate-950 disabled:cursor-not-allowed disabled:opacity-60"
          onClick={handleGenerateResume}
          disabled={isGenerating}
        >
          <Copy size={18} />
          {isGenerating ? "Generating resume..." : "Generate Resume"}
        </button>

        {resumeError && (
          <p className="mt-4 rounded-lg border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-red-200">
            {resumeError}
          </p>
        )}

        {generatedResume && (
          <div className="mt-4 rounded-lg border border-white/10 bg-black/20 p-4">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
              <h3 className="font-semibold text-white">Generated Resume</h3>
              <button
                className="focus-ring inline-flex items-center gap-2 rounded-lg border border-accent/40 bg-accent/10 px-3 py-2 text-sm font-semibold text-accent transition hover:bg-accent/20 disabled:cursor-not-allowed disabled:opacity-60"
                onClick={handleDownloadWord}
                disabled={isGenerating}
              >
                <Download size={16} />
                {isGenerating ? "Preparing download..." : "Download Word"}
              </button>
            </div>
            <pre className="max-h-[480px] overflow-auto whitespace-pre-wrap rounded-md bg-slate-950/80 p-4 text-sm leading-6 text-slate-200">
              {generatedResume}
            </pre>
          </div>
        )}
      </Panel>

      <Panel title="Parsing Pipeline">
        {["Extract text", "Detect skills", "Rank proficiency", "Generate career graph"].map((item, index) => (
          <div key={item} className="flex gap-4 border-b border-white/10 py-4 last:border-0">
            <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-white/10 text-sm font-semibold text-accent">{index + 1}</span>
            <div>
              <h3 className="font-semibold text-white">{item}</h3>
              <p className="text-sm text-slate-400">Mapped to resume parsing and recommendation requirements.</p>
            </div>
          </div>
        ))}
        <div className="mt-5 flex items-center gap-3 rounded-lg border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
          <FileText size={18} className="text-accent" />
          API contract: `POST /api/resume/upload`
        </div>
      </Panel>
    </div>
  );
}
