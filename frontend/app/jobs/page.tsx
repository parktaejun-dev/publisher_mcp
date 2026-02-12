'use client';

import { useState, useEffect } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function JobsPage() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchJobs = async () => {
    try {
      const res = await fetch(`${API_URL}/api/jobs`);
      const data = await res.json();
      setJobs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleRetry = async (jobId: string) => {
    try {
      await fetch(`${API_URL}/api/jobs/${jobId}/retry`, { method: 'POST' });
      fetchJobs();
    } catch (err) {
      alert("Failed to retry job");
    }
  };

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      <div className="px-4 py-5 sm:px-6 flex justify-between">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Ingest Jobs</h3>
        <button onClick={fetchJobs} className="text-sm text-blue-600 hover:text-blue-500">Refresh</button>
      </div>
      <ul className="divide-y divide-gray-200">
        {jobs.map((job) => (
          <li key={job.id}>
            <div className="px-4 py-4 sm:px-6">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-blue-600 truncate">
                  Job ID: {job.id.substring(0, 8)}...
                </p>
                <div className="ml-2 flex-shrink-0 flex">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                    ${job.status === 'completed' || job.status === 'draft_saved' ? 'bg-green-100 text-green-800' :
                      job.status === 'failed' ? 'bg-red-100 text-red-800' :
                      job.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'}`}>
                    {job.status}
                  </span>
                </div>
              </div>
              <div className="mt-2 sm:flex sm:justify-between">
                <div className="sm:flex">
                  <p className="flex items-center text-sm text-gray-500">
                    Engine: {job.engine} | Attempt: {job.attempt}
                  </p>
                </div>
                <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                  <p>
                    Updated: {new Date(job.updated_at).toLocaleString()}
                  </p>
                </div>
              </div>
              {job.last_error && (
                <div className="mt-2 text-sm text-red-600 bg-red-50 p-2 rounded">
                  Error: {job.last_error}
                </div>
              )}
               {job.status === 'failed' && (
                <div className="mt-2">
                  <button onClick={() => handleRetry(job.id)} className="text-indigo-600 hover:text-indigo-900 text-sm font-medium">Retry</button>
                </div>
              )}
            </div>
          </li>
        ))}
        {jobs.length === 0 && !loading && <li className="px-4 py-4 text-gray-500">No jobs found.</li>}
      </ul>
    </div>
  );
}
