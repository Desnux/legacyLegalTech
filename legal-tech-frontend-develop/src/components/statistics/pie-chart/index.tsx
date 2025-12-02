'use client';

import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
} from 'chart.js';
import { Pie } from 'react-chartjs-2';
import { CaseTableData, LawyerOfficeData, StatisticsData } from '@/utils/test-data';
import { translatedEventNames } from '@/utils/event-types';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale);

interface PieChartProps {
  type: 'statistics' | 'case-table' | 'lawyer-office';
  title: string;
  data: StatisticsData[] | CaseTableData[] | LawyerOfficeData[];
}

export default function PieChart({ type, title, data }: PieChartProps) {
  let dataArray: StatisticsData[] | CaseTableData[] | LawyerOfficeData[] = [];
  let labels: string[] = [];
  if (type === 'statistics') {
    dataArray = data as StatisticsData[];
    labels = dataArray.map(item => `${item.end_amount ? `${item.start_amount} - ${item.end_amount}` : `Mayor a ${item.start_amount}`}`);
  } else if (type === 'case-table') {
    dataArray = data as CaseTableData[];
    labels = dataArray.map(item => `${translatedEventNames[item.event_type]}`);
  } else if (type === 'lawyer-office') {
    dataArray = data as LawyerOfficeData[];
    labels = dataArray.map(item => `${item.name}`);
  }
  
  const chartData = {
    labels: labels,
    datasets: [
      {
        data: data.map(item => item.quantity),
        backgroundColor: [
          '#0D9488', // teal-green
          '#1E3A8A', // petroleum-blue
          '#F59E0B', // soft-gold
          '#EF4444', // red-500
          '#8B5CF6', // purple-500
          '#10B981', // emerald-500
          '#F97316', // orange-500
          '#06B6D4', // cyan-500
        ],
        borderColor: [
          '#0F766E', // teal-700
          '#1E40AF', // blue-700
          '#D97706', // amber-600
          '#DC2626', // red-600
          '#7C3AED', // violet-600
          '#059669', // emerald-600
          '#EA580C', // orange-600
          '#0891B2', // cyan-600
        ],
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          padding: 20,
          usePointStyle: true,
          font: {
            size: 12,
            family: 'Inter, system-ui, sans-serif',
          },
          color: '#374151', // charcoal-gray
        },
      },
      tooltip: {
        backgroundColor: '#FFFFFF',
        titleColor: '#1F2937',
        bodyColor: '#374151',
        borderColor: '#D1D5DB',
        borderWidth: 1,
        cornerRadius: 8,
        callbacks: {
          label: function(context: any) {
            const label = context.label || '';
            const value = context.parsed;
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value} juicios (${percentage}%)`;
          },
        },
      },
    },
  };

  return (
    <div className="bg-pure-white rounded-2xl shadow-lg border border-medium-gray overflow-hidden">
      <div className="p-6">
        <h3 className="text-h3 font-semibold text-charcoal-gray mb-6 text-center">
          {title}
        </h3>
        <div className="h-80">
          <Pie data={chartData} options={options} />
        </div>
      </div>
    </div>
  );
} 