"use client";

import { formatCurrency } from "@/utils/currency";
import { StatisticsData } from "@/utils/test-data";

export default function CaseCount({ item }: { item: StatisticsData }) {

    const getRangeColor = (start_amount: string, end_amount: string) => {
        const value = start_amount + end_amount;
        switch (value) {
          case '0M50M':
            return 'text-teal-green';
          case '50M100M':
            return 'text-petroleum-blue';
          case '100M150M':
            return 'text-soft-gold';
          case '150M200M':
            return 'text-red-500';
          case '200M':
            return 'text-purple-500';
          default:
            return 'text-charcoal-gray';
        }
      }

    const getRangeBgColor = (start_amount: string, end_amount: string) => {
        const value = start_amount + end_amount;
        switch (value) {
          case '0M50M':
            return 'bg-teal-green/10';
          case '50M100M':
            return 'bg-petroleum-blue/10';
          case '100M150M':
            return 'bg-soft-gold/10';
          case '150M200M':
            return 'bg-red-50';
          case '200M':
            return 'bg-purple-50';
          default:
            return 'bg-light-gray';
        }
      }

  return (
    <div className="bg-pure-white rounded-2xl shadow-lg border border-medium-gray p-6 hover:shadow-xl transition-shadow duration-300 h-full">
      <div className="text-center">
        <div className={`rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4 ${getRangeBgColor(item.start_amount, item.end_amount)}`}>
          <div className={`w-3 h-3 rounded-full ${getRangeColor(item.start_amount, item.end_amount).replace('text-', 'bg-')}`}></div>
        </div>
        <h3 className="text-small font-semibold text-charcoal-gray mb-2">
          Rango {item.end_amount ? `${item.start_amount} - ${item.end_amount}` : `Mayor a ${item.start_amount}`}
        </h3>
        <div className={`text-h2 font-bold ${getRangeColor(item.start_amount, item.end_amount)} mb-2`}>
          {item.quantity}
        </div>
        <p className="text-body text-medium-gray mb-1">
          Juicios
        </p>
        <p className="text-small font-semibold text-charcoal-gray">
          {formatCurrency(item.amount)}
        </p>
      </div>
    </div>
  );
}