'use client';

import { useState, useEffect } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [formData, setFormData] = useState({
    media_owner: '',
    media_name: '',
    doc_type: 'media_kit',
    confidentiality: 'internal',
    doc_date: '',
    tags: ''
  });

  const fetchDocuments = async () => {
    try {
      const res = await fetch(`${API_URL}/api/documents`);
      const data = await res.json();
      setDocuments(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    const data = new FormData();
    data.append('file', file);
    Object.entries(formData).forEach(([key, value]) => {
        data.append(key, value);
    });

    try {
      const res = await fetch(`${API_URL}/api/documents`, {
        method: 'POST',
        body: data,
      });
      if (res.ok) {
        alert('Upload successful!');
        setFile(null);
        // Reset form or keep values? Keep values except file maybe.
        fetchDocuments();
      } else {
        const err = await res.json();
        alert(`Error: ${err.detail || 'Upload failed'}`);
      }
    } catch (err) {
      console.error(err);
      alert('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="bg-white shadow sm:rounded-lg p-6">
        <h2 className="text-lg font-medium leading-6 text-gray-900 mb-4">Upload Document</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div className="sm:col-span-3">
              <label className="block text-sm font-medium text-gray-700">Media Owner</label>
              <input required type="text" name="media_owner" value={formData.media_owner} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2" />
            </div>
            <div className="sm:col-span-3">
              <label className="block text-sm font-medium text-gray-700">Media Name</label>
              <input required type="text" name="media_name" value={formData.media_name} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2" />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700">Doc Type</label>
              <select name="doc_type" value={formData.doc_type} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2">
                <option value="media_kit">Media Kit</option>
                <option value="rate_card">Rate Card</option>
                <option value="proposal">Proposal</option>
                <option value="etc">Etc</option>
              </select>
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700">Confidentiality</label>
              <select name="confidentiality" value={formData.confidentiality} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2">
                <option value="public">Public</option>
                <option value="internal">Internal</option>
                <option value="restricted">Restricted</option>
              </select>
            </div>
             <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700">Doc Date</label>
              <input type="date" name="doc_date" value={formData.doc_date} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2" />
            </div>
             <div className="sm:col-span-6">
              <label className="block text-sm font-medium text-gray-700">Tags (comma separated)</label>
              <input type="text" name="tags" value={formData.tags} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2" />
            </div>
            <div className="sm:col-span-6">
              <label className="block text-sm font-medium text-gray-700">File (PDF/PPTX)</label>
              <input required type="file" onChange={handleFileChange} className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />
            </div>
          </div>
          <div className="flex justify-end">
            <button type="submit" disabled={uploading} className="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none disabled:opacity-50">
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </div>
        </form>
      </div>

      <div className="bg-white shadow sm:rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Documents</h3>
        </div>
        <div className="border-t border-gray-200">
            {loading ? <p className="p-4">Loading...</p> : (
            <ul className="divide-y divide-gray-200">
                {documents.map((doc) => (
                <li key={doc.id} className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                        <div className="text-sm font-medium text-blue-600 truncate">{doc.original_filename}</div>
                        <div className="ml-2 flex-shrink-0 flex">
                            <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">{doc.doc_type}</span>
                        </div>
                    </div>
                    <div className="mt-2 sm:flex sm:justify-between">
                        <div className="sm:flex">
                            <p className="flex items-center text-sm text-gray-500">
                                {doc.media_owner} / {doc.media_name}
                            </p>
                        </div>
                         <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                            <p>Created: {new Date(doc.created_at).toLocaleDateString()}</p>
                        </div>
                    </div>
                </li>
                ))}
            </ul>
            )}
        </div>
      </div>
    </div>
  );
}
