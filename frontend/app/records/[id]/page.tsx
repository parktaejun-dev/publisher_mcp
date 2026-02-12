'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function RecordDetailPage() {
  const { id } = useParams();
  const router = useRouter();

  const [draft, setDraft] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [jsonText, setJsonText] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [approving, setApproving] = useState(false);

  useEffect(() => {
    if (!id) return;
    async function fetchDraft() {
      try {
        const res = await fetch(`${API_URL}/api/records/draft/${id}`);
        if (!res.ok) throw new Error('Failed to fetch draft');
        const data = await res.json();
        setDraft(data);
        setJsonText(JSON.stringify(data.raw_json, null, 2));
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchDraft();
  }, [id]);

  const saveDraft = async () => {
    setSaving(true);
    setError('');
    try {
      const parsed = JSON.parse(jsonText);
      const res = await fetch(`${API_URL}/api/records/draft/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsed),
      });
      if (!res.ok) throw new Error('Failed to save');
      const updated = await res.json();
      setDraft(updated);
      return true;
    } catch (err: any) {
      setError(err.message);
      alert('Save failed: ' + err.message);
      return false;
    } finally {
      setSaving(false);
    }
  };

  const handleSave = async () => {
      const success = await saveDraft();
      if (success) alert('Saved successfully');
  };

  const handleApprove = async () => {
    setApproving(true);
    setError('');
    try {
        // First save any changes
        const saved = await saveDraft();
        if (!saved) return;

        const res = await fetch(`${API_URL}/api/records/draft/${id}/approve`, {
            method: 'POST'
        });

        if (!res.ok) throw new Error('Failed to approve');
        const approvedRecord = await res.json();
        alert('Approved! Record ID: ' + approvedRecord.id);
        router.push('/records'); // Go back to list
    } catch (err: any) {
        setError(err.message);
        alert('Approval failed: ' + err.message);
    } finally {
        setApproving(false);
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (error) return <div className="p-8 text-red-600">Error: {error}</div>;
  if (!draft) return <div className="p-8">Draft not found</div>;

  return (
    <div className="bg-white shadow sm:rounded-lg p-6 space-y-6">
      <div className="flex justify-between items-center border-b pb-4">
        <h2 className="text-xl font-bold text-gray-900">Draft Editor: {draft.id.substring(0, 8)}...</h2>
        <div className="space-x-4">
            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                    ${draft.status === 'draft_saved' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {draft.status}
            </span>
        </div>
      </div>

      {draft.validation_report && (
          <div className="bg-gray-50 p-4 rounded-md text-sm">
              <h4 className="font-semibold mb-2">Validation Report</h4>
              <p>Valid: {draft.validation_report.valid ? 'Yes' : 'No'}</p>
              <p>Evidence Count: {draft.validation_report.evidence_count}</p>
              {draft.validation_report.errors && draft.validation_report.errors.length > 0 && (
                  <ul className="list-disc list-inside text-red-600 mt-2">
                      {draft.validation_report.errors.map((e: string, i: number) => <li key={i}>{e}</li>)}
                  </ul>
              )}
          </div>
      )}

      <div>
        <label htmlFor="json-editor" className="block text-sm font-medium text-gray-700 mb-2">
          Raw JSON (Edit carefully)
        </label>
        <textarea
          id="json-editor"
          rows={20}
          className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md font-mono"
          value={jsonText}
          onChange={(e) => setJsonText(e.target.value)}
        />
      </div>

      <div className="flex justify-end space-x-4 pt-4 border-t">
        <button
          onClick={handleSave}
          disabled={saving || approving}
          className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none disabled:opacity-50"
        >
          {saving ? 'Saving...' : 'Save Draft'}
        </button>
        <button
          onClick={handleApprove}
          disabled={saving || approving}
          className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none disabled:opacity-50"
        >
          {approving ? 'Approving...' : 'Approve & Create Record'}
        </button>
      </div>
    </div>
  );
}
