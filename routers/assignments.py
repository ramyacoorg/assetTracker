// app/assignments/page.tsx
"use client";
import { useEffect, useState } from "react";
import api from "@/lib/api";

export default function AssignmentsPage() {
  const [assignments, setAssignments] = useState<any[]>([]);
  const [availableAssets, setAvailableAssets] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ asset_id: "", employee_id: "" });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const fetchAll = async () => {
    try {
      const [asgRes, assetRes, userRes] = await Promise.all([
        api.get("/api/assignments/"),
        api.get("/api/assets/"),
        api.get("/api/users/"),
      ]);
      setAssignments(asgRes.data);
      setAvailableAssets(assetRes.data.filter((a: any) => a.asset_status === "available"));
      setUsers(userRes.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const handleAssign = async () => {
    if (!form.asset_id || !form.employee_id) {
      setError("Please select both asset and employee.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await api.post("/api/assignments/assign", {
        asset_id: parseInt(form.asset_id),
        employee_id: parseInt(form.employee_id),
      });
      setShowModal(false);
      setForm({ asset_id: "", employee_id: "" });
      fetchAll();
    } catch (e: any) {
      setError(e.response?.data?.detail || "Failed to assign asset.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleReturn = async (id: number) => {
    if (!confirm("Mark this asset as returned?")) return;
    try {
      await api.patch(`/api/assignments/${id}/return`);
      fetchAll();
    } catch (e) {
      alert("Failed to return asset.");
    }
  };

  const statusColor: Record<string, string> = {
    active: "#10b981",
    returned: "#f59e0b",
  };

  return (
    <div style={{ minHeight: "100vh", background: "linear-gradient(135deg,#1e1b4b,#0f172a)", padding: "2rem", fontFamily: "sans-serif" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ color: "#e0e7ff", fontSize: "1.75rem", fontWeight: 700, margin: 0 }}>Assignments</h1>
          <p style={{ color: "rgba(255,255,255,0.4)", fontSize: "0.875rem", margin: "4px 0 0" }}>Track asset assignments</p>
        </div>
        <button
          onClick={() => { setShowModal(true); setError(""); }}
          style={{ background: "linear-gradient(135deg,#6366f1,#8b5cf6)", color: "#fff", border: "none", borderRadius: "0.75rem", padding: "0.75rem 1.25rem", fontWeight: 600, cursor: "pointer", fontSize: "0.875rem" }}
        >
          + Assign Asset
        </button>
      </div>

      {loading ? (
        <p style={{ color: "rgba(255,255,255,0.4)" }}>Loading...</p>
      ) : assignments.length === 0 ? (
        <p style={{ color: "rgba(255,255,255,0.4)", textAlign: "center", marginTop: "4rem" }}>No assignments yet.</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {assignments.map((a) => (
            <div key={a.id} style={{ background: "rgba(255,255,255,0.07)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "1rem", padding: "1rem 1.25rem", display: "flex", alignItems: "center", gap: "1rem" }}>
              <div style={{ width: 44, height: 44, borderRadius: "0.75rem", background: "linear-gradient(135deg,#6366f1,#8b5cf6)", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, color: "#fff", fontSize: "1rem", flexShrink: 0 }}>
                {a.employee_name?.charAt(0).toUpperCase()}
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ color: "#e2e8f0", fontWeight: 600, margin: 0, fontSize: "0.9rem" }}>{a.employee_name}</p>
                <p style={{ color: "#6366f1", fontSize: "0.8rem", margin: "2px 0 0" }}>
                  {a.asset_name} · <span style={{ color: "rgba(255,255,255,0.4)" }}>{a.asset_code}</span>
                </p>
              </div>
              <div style={{ textAlign: "right" }}>
                <span style={{ fontSize: "0.7rem", padding: "3px 10px", borderRadius: "999px", fontWeight: 600, background: a.status === "active" ? "rgba(16,185,129,0.15)" : "rgba(245,158,11,0.15)", color: statusColor[a.status] || "#94a3b8" }}>
                  {a.status === "active" ? "Active" : "Returned"}
                </span>
                <p style={{ color: "rgba(255,255,255,0.3)", fontSize: "0.7rem", margin: "4px 0 0" }}>{a.assigned_date}</p>
              </div>
              {a.status === "active" && (
                <button
                  onClick={() => handleReturn(a.id)}
                  style={{ background: "rgba(244,63,94,0.15)", color: "#fb7185", border: "1px solid rgba(244,63,94,0.3)", borderRadius: "0.5rem", padding: "4px 10px", fontSize: "0.7rem", cursor: "pointer", fontWeight: 500 }}
                >
                  Return
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Assign Modal */}
      {showModal && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 50, padding: "1rem" }}>
          <div style={{ background: "#1e293b", borderRadius: "1.25rem", padding: "2rem", width: "100%", maxWidth: "420px", border: "1px solid rgba(255,255,255,0.1)" }}>
            <h2 style={{ color: "#e2e8f0", fontWeight: 700, fontSize: "1.25rem", margin: "0 0 1.5rem" }}>Assign Asset</h2>

            <label style={{ color: "rgba(255,255,255,0.6)", fontSize: "0.8rem", display: "block", marginBottom: "6px" }}>Select Asset (Available Only)</label>
            <select
              value={form.asset_id}
              onChange={(e) => setForm({ ...form, asset_id: e.target.value })}
              style={{ width: "100%", padding: "0.75rem", borderRadius: "0.75rem", background: "rgba(255,255,255,0.07)", border: "1px solid rgba(255,255,255,0.15)", color: "#e2e8f0", marginBottom: "1rem", fontSize: "0.875rem" }}
            >
              <option value="" style={{ background: "#1e293b" }}>-- Select Asset --</option>
              {availableAssets.map((asset) => (
                <option key={asset.id} value={asset.id} style={{ background: "#1e293b" }}>
                  {asset.asset_name} ({asset.asset_code})
                </option>
              ))}
            </select>

            <label style={{ color: "rgba(255,255,255,0.6)", fontSize: "0.8rem", display: "block", marginBottom: "6px" }}>Select Employee</label>
            <select
              value={form.employee_id}
              onChange={(e) => setForm({ ...form, employee_id: e.target.value })}
              style={{ width: "100%", padding: "0.75rem", borderRadius: "0.75rem", background: "rgba(255,255,255,0.07)", border: "1px solid rgba(255,255,255,0.15)", color: "#e2e8f0", marginBottom: "1rem", fontSize: "0.875rem" }}
            >
              <option value="" style={{ background: "#1e293b" }}>-- Select Employee --</option>
              {users.map((u) => (
                <option key={u.id} value={u.id} style={{ background: "#1e293b" }}>
                  {u.full_name} ({u.email})
                </option>
              ))}
            </select>

            {error && <p style={{ color: "#fb7185", fontSize: "0.8rem", marginBottom: "1rem" }}>{error}</p>}

            <div style={{ display: "flex", gap: "0.75rem" }}>
              <button
                onClick={() => setShowModal(false)}
                style={{ flex: 1, padding: "0.75rem", borderRadius: "0.75rem", background: "rgba(255,255,255,0.07)", border: "1px solid rgba(255,255,255,0.1)", color: "#94a3b8", cursor: "pointer", fontWeight: 500 }}
              >
                Cancel
              </button>
              <button
                onClick={handleAssign}
                disabled={submitting}
                style={{ flex: 2, padding: "0.75rem", borderRadius: "0.75rem", background: submitting ? "rgba(99,102,241,0.5)" : "linear-gradient(135deg,#6366f1,#8b5cf6)", border: "none", color: "#fff", cursor: submitting ? "not-allowed" : "pointer", fontWeight: 600 }}
              >
                {submitting ? "Assigning..." : "Confirm Assign"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
