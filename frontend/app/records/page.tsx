'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function RecordsPage() {
  const [kind, setKind] = useState<'draft' | 'approved'>('draft');
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function fetchRecords() {
      setLoading(true);
      try {
        const res = await fetch(`${API_URL}/api/records?kind=${kind}`);
        const data = await res.json();
        setRecords(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchRecords();
  }, [kind]);

  return (
    <div className="bg-white shadow sm:rounded-lg">
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex" aria-label="Tabs">
          <button
            onClick={() => setKind('draft')}
            className={`${kind === 'draft' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} w-1/2 py-4 px-1 text-center border-b-2 font-medium text-sm`}
          >
            Drafts
          </button>
          <button
            onClick={() => setKind('approved')}
            className={`${kind === 'approved' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} w-1/2 py-4 px-1 text-center border-b-2 font-medium text-sm`}
          >
            Approved Records
          </button>
        </nav>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {loading && <li className="px-4 py-4 text-gray-500">Loading...</li>}
          {!loading && records.length === 0 && <li className="px-4 py-4 text-gray-500">No records found.</li>}
          {!loading && records.map((record) => (
            <li key={record.id}>
              <div className="block hover:bg-gray-50">
                <div className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-blue-600 truncate">
                      {kind === 'draft' ?
                        <Link href={`/records/${record.id}`}>Draft: {record.id.substring(0, 8)}...</Link> :
                        `Record: ${record.media_owner} / ${record.media_name}`}
                    </p>
                    <div className="ml-2 flex-shrink-0 flex">
                      <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        {kind === 'draft' ? record.status : 'Approved'}
                      </p>
                    </div>
                  </div>
                  <div className="mt-2 sm:flex sm:justify-between">
                    <div className="sm:flex">
                      <p className="flex items-center text-sm text-gray-500">
                        {kind === 'draft' ? `Engine: ${record.engine}` : `Type: ${record.media_type}`}
                      </p>
                    </div>
                    <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                      <p>
                        Created: {new Date(record.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                   {kind === 'draft' && (
                       <div className="mt-2">
                            <Link href={`/records/${record.id}`} className="text-indigo-600 hover:text-indigo-900 text-sm font-medium">Review & Approve</Link>
                       </div>
                   )}
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
