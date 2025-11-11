
import type { FileProcessResult } from '../types/document';


export const convertToCSV = (results: FileProcessResult[]): string => {
  const headers = [
    'Filename',
    'First Name',
    'Middle Name',
    'Last Name',
    'Date Created',
    'DOC #',
    'Facility Name',
    'Address',
    'Unit',
    'AI Summary',
    'Raw Text',
    'Status',
    'Error'
  ];

  const rows = results.map(result => {
    if (result.success && result.data) {
      return [
        result.filename,
        result.data.first_name,
        result.data.middle_name || '',
        result.data.last_name,
        result.data.date_created,
        result.data.doc_number,
        result.data.facility_name,
        result.data.address,
        result.data.unit || '',
        result.data.ai_summary,
        result.data.raw_text,
        'Success',
        ''
      ];
    } else {
      return [
        result.filename,
        '', '', '', '', '', '', '', '', '', '',
        'Failed',
        result.error || 'Unknown error'
      ];
    }
  });

  const escapeCSV = (value: string): string => {
    if (value === null || value === undefined) return '';
    const stringValue = String(value);
    if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
      return `"${stringValue.replace(/"/g, '""')}"`;
    }
    return stringValue;
  };

  const csvContent = [
    headers.map(escapeCSV).join(','),
    ...rows.map(row => row.map(escapeCSV).join(','))
  ].join('\n');

  return csvContent;
};

export const downloadCSV = (results: FileProcessResult[], filename: string = 'extracted-data.csv') => {
  const csvContent = convertToCSV(results);
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
};

export const downloadExcel = async (results: FileProcessResult[], filename: string = 'extracted-data.xlsx') => {
  const XLSX = await import('xlsx');
  
  const headers = [
    'Filename',
    'First Name',
    'Middle Name',
    'Last Name',
    'Date Created',
    'DOC #',
    'Facility Name',
    'Address',
    'Unit',
    'AI Summary',
    'Raw Text',
    'Status',
    'Error'
  ];

  const rows = results.map(result => {
    if (result.success && result.data) {
      return [
        result.filename,
        result.data.first_name,
        result.data.middle_name || '',
        result.data.last_name,
        result.data.date_created,
        result.data.doc_number,
        result.data.facility_name,
        result.data.address,
        result.data.unit || '',
        result.data.ai_summary,
        result.data.raw_text,
        'Success',
        ''
      ];
    } else {
      return [
        result.filename,
        '', '', '', '', '', '', '', '', '', '',
        'Failed',
        result.error || 'Unknown error'
      ];
    }
  });

  const wsData = [headers, ...rows];
  const ws = XLSX.utils.aoa_to_sheet(wsData);

  ws['!cols'] = [
    { wch: 30 }, 
    { wch: 15 },
    { wch: 15 },
    { wch: 15 },
    { wch: 12 },
    { wch: 12 },
    { wch: 30 },
    { wch: 40 },
    { wch: 10 },
    { wch: 50 },
    { wch: 50 },
    { wch: 10 },
    { wch: 30 }
  ];

  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Extracted Data');

  XLSX.writeFile(wb, filename);
};