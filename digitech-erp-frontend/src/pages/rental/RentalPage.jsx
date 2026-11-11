import React, { useEffect, useMemo, useState } from "react";
import html2pdf from "html2pdf.js";
import {
  Search,
  RefreshCw,
  Users,
  Printer,
  Save,
  RotateCcw,
  CalendarDays,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  X,
  CheckCircle2,
  Clock3,
  IndianRupee,
  Plus,
  FileText,
  Download,
  Eye,
  Pencil,
  Trash2,
} from "lucide-react";
import { toast } from "react-toastify";
import api from "../../api/axios";
import Sidebar from "../../components/layout/Sidebar/Sidebar";
import Navbar from "../../components/layout/Navbar/Navbar";
import CustomerForm from "../../components/customer/CustomerForm/CustomerForm";
import { useCustomers } from "../../context/CustomerContext";
import "./RentalPage.css";

const getApiErrorMessage = (error, fallback) => {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) =>
        typeof item === "string"
          ? item
          : item?.msg || item?.message || "Invalid value"
      )
      .join(", ");
  }
  if (typeof detail === "string") return detail;
  if (typeof error?.response?.data?.message === "string") {
    return error.response.data.message;
  }
  if (typeof error?.response?.data?.detail === "string") {
    return error.response.data.detail;
  }
  if (typeof error?.response?.data?.data?.message === "string") {
    return error.response.data.data.message;
  }
  return error?.message || fallback;
};

const extractArray = (data, keys = []) => {
  if (Array.isArray(data)) return data;
  for (const key of keys) {
    if (Array.isArray(data?.[key])) return data[key];
  }
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.results)) return data.results;
  return [];
};

const firstValue = (...values) => {
  const found = values.find(
    (value) =>
      value !== undefined &&
      value !== null &&
      String(value).trim() !== ""
  );
  return found === undefined || found === null ? "" : String(found);
};

const getCurrentMonth = () => {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
};

const getCustomerName = (customer) =>
  firstValue(
    customer?.customer_name,
    customer?.name,
    customer?.company_name,
    customer?.business_name,
    customer?.contact_person,
    `Customer ${customer?.id ?? ""}`
  );

const getCustomerCode = (customer) =>
  firstValue(customer?.customer_code, customer?.code);

const getCustomerPhone = (customer) =>
  firstValue(
    customer?.phone,
    customer?.mobile,
    customer?.mobile_number,
    customer?.phone_number
  );

const getCustomerEmail = (customer) =>
  firstValue(customer?.email, customer?.email_address);

const getCustomerAddress = (customer) =>
  [
    customer?.billing_address,
    customer?.city,
    customer?.state,
    customer?.country,
    customer?.pincode,
  ]
    .filter((value) => value != null && String(value).trim() !== "")
    .join(", ") ||
  firstValue(customer?.address, customer?.full_address, customer?.location);

const getCustomerWebsite = (customer) => firstValue(customer?.website);
const getCustomerPAN = (customer) => firstValue(customer?.pan);
const getCustomerContactPerson = (customer) => firstValue(customer?.contact_person);
const getCustomerShippingAddress = (customer) => firstValue(customer?.shipping_address);
const getCustomerCreditLimit = (customer) => Number(customer?.credit_limit ?? 0) || 0;
const getCustomerCreditDays = (customer) => Number(customer?.credit_days ?? 0) || 0;
const getCustomerOpeningBalance = (customer) => Number(customer?.opening_balance ?? 0) || 0;
const getCustomerCurrentBalance = (customer) => Number(customer?.current_balance ?? 0) || 0;

const getMachineName = (machine) =>
  firstValue(
    machine?.machine_name,
    machine?.model_name,
    machine?.model,
    machine?.product_name,
    machine?.name,
    machine?.machine_number,
    "Machine"
  );

const getMachineNumber = (machine) =>
  firstValue(
    machine?.machine_number,
    machine?.machine_id,
    machine?.machine_no,
    machine?.id
  );

const getMachineSerial = (machine) =>
  firstValue(machine?.serial_number, machine?.serialNumber, "—");

const getMachineReading = (machine) =>
  Number(
    machine?.current_meter ??
      machine?.currentMeter ??
      machine?.current_reading ??
      machine?.currentReading ??
      0
  ) || 0;

const getOpeningReading = (machine) =>
  Number(machine?.opening_meter ?? machine?.openingMeter ?? 0) || 0;

const getMachinePrice = (machine) =>
  Number(
    machine?.cost_per_copy ??
      machine?.costPerCopy ??
      machine?.rate_per_copy ??
      machine?.ratePerCopy ??
      0
  ) || 0;

const getBillMachineId = (bill) =>
  bill?.machine_id ?? bill?.machineId ?? null;

const getBillMonth = (bill) =>
  String(bill?.billing_month ?? bill?.billingMonth ?? "");

const getBillPrevious = (bill, fallback = 0) =>
  Number(
    bill?.previous_meter ??
      bill?.previousMeter ??
      bill?.previous_reading ??
      bill?.previousReading ??
      fallback
  ) || 0;

const getBillCurrent = (bill, fallback = 0) =>
  Number(
    bill?.current_meter ??
      bill?.currentMeter ??
      bill?.current_reading ??
      bill?.currentReading ??
      fallback
  ) || 0;

const getBillPrice = (bill, fallback = 0) =>
  Number(
    bill?.cost_per_copy ??
      bill?.costPerCopy ??
      bill?.rate_per_copy ??
      bill?.ratePerCopy ??
      fallback
  ) || 0;

const getBillCopies = (bill, previous, current) =>
  Number(
    bill?.copies_used ??
      bill?.copiesUsed ??
      Math.max(current - previous, 0)
  ) || 0;

const getBillAmount = (bill, copies, price) =>
  Number(
    bill?.total_amount ??
      bill?.totalAmount ??
      bill?.amount ??
      copies * price
  ) || 0;

const getBillStatus = (bill) =>
  firstValue(
    bill?.status,
    bill?.payment_status,
    bill?.paymentStatus,
    bill?.reading_status,
    "Submitted"
  );

const normalizePaymentStatus = (status) => {
  const value = String(status || "").trim().toUpperCase();
  return value === "RECEIVED" ||
    value === "PAID" ||
    value === "PAYMENT_RECEIVED"
    ? "RECEIVED"
    : "PENDING";
};

const isReadingUpdated = (row) => {
  const newReading = Number(
    row?.monthlyReading ??
      row?.newReading ??
      row?.new_reading ??
      row?.currentReading ??
      row?.current_reading ??
      row?.reading ??
      0
  );
  const oldReading = Number(
    row?.previousReading ??
      row?.oldReading ??
      row?.old_reading ??
      row?.previous_reading ??
      0
  );
  return Number.isFinite(newReading) && newReading > oldReading;
};

const formatMoney = (value) =>
  `₹ ${(Number(value) || 0).toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;

const formatNumber = (value) =>
  (Number(value) || 0).toLocaleString("en-IN");

const monthLabel = (month) => {
  if (!month) return "—";
  const [year, m] = String(month).split("-");
  const date = new Date(Number(year), Number(m) - 1, 1);
  if (Number.isNaN(date.getTime())) return month;
  return date.toLocaleDateString("en-IN", {
    month: "short",
    year: "numeric",
  });
};

const getInitials = (name) =>
  String(name || "C")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();


const getMachineFixedRent = (machine) =>
  Number(
    machine?.rental_rate ??
      machine?.fixed_rent ??
      machine?.fixed_rental_amount ??
      machine?.rental_amount ??
      machine?.monthly_rent ??
      machine?.fixedRent ??
      0
  ) || 0;

const getMachineRentalAdvance = (machine) =>
  Number(machine?.rental_advance ?? 0) || 0;

const getMachineFreeCopies = (machine) =>
  Number(
    machine?.free_prints_per_month ??
      machine?.free_copies_per_month ??
      machine?.free_copies ??
      machine?.free_prints ??
      machine?.freeCopies ??
      0
  ) || 0;

const getMachineA4BWRate = (machine) => Number(machine?.a4_bw_rate ?? 0) || 0;
const getMachineA4ColorRate = (machine) => Number(machine?.a4_color_rate ?? 0) || 0;
const getMachineA3BWRate = (machine) => Number(machine?.a3_bw_rate ?? 0) || 0;
const getMachineA3ColorRate = (machine) => Number(machine?.a3_color_rate ?? 0) || 0;

const getMachineExtraRate = (machine) =>
  Number(machine?.cost_per_copy ?? machine?.rate_per_copy ?? 0) || 0;

const getCustomerGSTIN = (customer) =>
  firstValue(
    customer?.gstin,
    customer?.gst_number,
    customer?.gst_no,
    customer?.tax_number
  );

const formatDateISO = (date) => {
  const d = new Date(date);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};

const addDaysToDate = (dateValue, days = 15) => {
  const date = new Date(`${dateValue}T12:00:00`);
  date.setDate(date.getDate() + days);
  return formatDateISO(date);
};

// Format: DISRB + year + month + day + running number, e.g. DISRB-20261017-0001.
const makeInvoiceNumber = (_month, sequence = 1, dateValue = formatDateISO(new Date())) => {
  const datePart = String(dateValue || formatDateISO(new Date())).replace(/-/g, "");
  return `DISRB-${datePart}-${String(sequence).padStart(4, "0")}`;
};

const RENTAL_PRINT_TYPES = [
  { key: "a4_bw", label: "A4 Black & White", rateKey: "a4_bw_rate", meterKey: "a4_bw_current_meter", freeKey: "a4_bw_free_copies" },
  { key: "a4_color", label: "A4 Color", rateKey: "a4_color_rate", meterKey: "a4_color_current_meter", freeKey: "a4_color_free_copies" },
  { key: "a3_bw", label: "A3 Black & White", rateKey: "a3_bw_rate", meterKey: "a3_bw_current_meter", freeKey: "a3_bw_free_copies" },
  { key: "a3_color", label: "A3 Color", rateKey: "a3_color_rate", meterKey: "a3_color_current_meter", freeKey: "a3_color_free_copies" },
];

const getPrintPreviousReading = (machine, key) => {
  const type = RENTAL_PRINT_TYPES.find((item) => item.key === key);
  const value = type ? machine?.[type.meterKey] : 0;
  return Math.max(Number(value) || 0, 0);
};

const getMachineFreeCopiesForType = (machine, key) => {
  const type = RENTAL_PRINT_TYPES.find((item) => item.key === key);
  const raw = type?.freeKey ? machine?.[type.freeKey] : 0;
  // Legacy fallback is used only if the new per-type field is absent.
  const legacy = machine?.free_prints_per_month ?? machine?.free_copies_per_month ?? 0;
  return Math.max(Number(raw ?? legacy) || 0, 0);
};

const calculateRentalBill = ({ machine, readings, gstPercent, previousReadings = null }) => {
  const printBreakdown = RENTAL_PRINT_TYPES.map((type) => {
    const previous = previousReadings && previousReadings[type.key] != null
      ? Math.max(Number(previousReadings[type.key]) || 0, 0)
      : getPrintPreviousReading(machine, type.key);
    const rawCurrent = readings?.[type.key];
    const current = rawCurrent === "" || rawCurrent == null
      ? previous
      : Math.max(Number(rawCurrent) || 0, 0);
    const copies = Math.max(current - previous, 0);
    const rate = Math.max(Number(machine?.[type.rateKey]) || 0, 0);
    const allowance = getMachineFreeCopiesForType(machine, type.key);
    const freeCopies = Math.min(copies, allowance);
    const chargeableCopies = Math.max(copies - freeCopies, 0);
    const amount = Math.round(chargeableCopies * rate * 100) / 100;
    return { ...type, previous, current, copies, rate, allowance, freeCopies, chargeableCopies, amount };
  });

  const usedCopies = printBreakdown.reduce((sum, type) => sum + type.copies, 0);
  const freeAllowance = printBreakdown.reduce((sum, type) => sum + type.allowance, 0);
  const freeCopies = printBreakdown.reduce((sum, type) => sum + type.freeCopies, 0);
  const chargeableCopies = printBreakdown.reduce((sum, type) => sum + type.chargeableCopies, 0);
  const copyCharges = Math.round(printBreakdown.reduce((sum, type) => sum + type.amount, 0) * 100) / 100;
  const fixedRent = Math.max(Number(getMachineFixedRent(machine)) || 0, 0);
  const subtotal = Math.round((fixedRent + copyCharges) * 100) / 100;
  const safeGstPercent = Math.max(Number(gstPercent) || 0, 0);
  const gstAmount = Math.round((subtotal * safeGstPercent / 100) * 100) / 100;
  const grandTotal = Math.round((subtotal + gstAmount) * 100) / 100;
  const previousReading = printBreakdown.reduce((sum, type) => sum + type.previous, 0);
  const currentReading = printBreakdown.reduce((sum, type) => sum + type.current, 0);

  return {
    printBreakdown,
    previousReading,
    currentReading,
    usedCopies,
    freeCopies,
    freeAllowance,
    chargeableCopies,
    fixedRent,
    copyCharges,
    subtotal,
    gstPercent: safeGstPercent,
    gstAmount,
    grandTotal,
  };
};

export default function RentalPage() {
  const {
    selectedCustomer: customerFormSelection,
    setSelectedCustomer,
  } = useCustomers();

  const [customerFormWasOpen, setCustomerFormWasOpen] = useState(false);
  const [pendingNewCustomerName, setPendingNewCustomerName] = useState("");

  const [activeRentalTab, setActiveRentalTab] = useState("invoices");
  const [customers, setCustomers] = useState([]);
  const [machines, setMachines] = useState([]);
  const [rentalBills, setRentalBills] = useState([]);

  const [searchText, setSearchText] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");
  const [paymentFilter, setPaymentFilter] = useState("ALL");
  const [readingFilter, setReadingFilter] = useState("ALL");
  const [billingMonth, setBillingMonth] = useState(getCurrentMonth());
  const [activeBillingMonth, setActiveBillingMonth] = useState(getCurrentMonth());

  const [selectedCustomerId, setSelectedCustomerId] = useState(null);
  const [selectedMachineId, setSelectedMachineId] = useState(null);

  // -----------------------------------------------------
  // Rental invoice / bill UI
  // -----------------------------------------------------
  const [billDrawerOpen, setBillDrawerOpen] = useState(false);
  const [editingInvoice, setEditingInvoice] = useState(null);
  const [deletingBillId, setDeletingBillId] = useState(null);
  const [billCustomerId, setBillCustomerId] = useState("");
  const [billCustomerSearch, setBillCustomerSearch] = useState("");
  const [billCustomerSearchOpen, setBillCustomerSearchOpen] = useState(false);
  const [billMachineId, setBillMachineId] = useState("");
  const [billCurrentReading, setBillCurrentReading] = useState("");
  const [billPrintReadings, setBillPrintReadings] = useState({
    a4_bw: "", a4_color: "", a3_bw: "", a3_color: "",
  });
  const [billGSTPercent, setBillGSTPercent] = useState("18");
  const [billBillingMonth, setBillBillingMonth] = useState(getCurrentMonth());
  const [generatedInvoices, setGeneratedInvoices] = useState([]);
  const [invoicePreview, setInvoicePreview] = useState(null);
  const [invoiceSearchInput, setInvoiceSearchInput] = useState("");
  const [invoiceSearchText, setInvoiceSearchText] = useState("");
  const [invoiceSearchLoading, setInvoiceSearchLoading] = useState(false);
  const [visibleInvoiceCount, setVisibleInvoiceCount] = useState(25);
  const [generatingInvoice, setGeneratingInvoice] = useState(false);

  // Debounced live invoice search: updates automatically while typing.
  useEffect(() => {
    setInvoiceSearchLoading(true);
    const timer = window.setTimeout(() => {
      setInvoiceSearchText(invoiceSearchInput.trim());
      setInvoiceSearchLoading(false);
    }, 300);

    return () => window.clearTimeout(timer);
  }, [invoiceSearchInput]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const [draftReadings, setDraftReadings] = useState({});
  const [draftPrices, setDraftPrices] = useState({});
  const [draftPaymentStatuses, setDraftPaymentStatuses] = useState({});
  const [savingMachineId, setSavingMachineId] = useState(null);

  const [rolloverModalOpen, setRolloverModalOpen] = useState(false);
  const [rolloverTargetMonth, setRolloverTargetMonth] = useState("");
  const [rolloverDoneForMonth, setRolloverDoneForMonth] = useState({});
  const [rollingOver, setRollingOver] = useState(false);

  const loadRentalData = async (showRefresh = false) => {
    try {
      if (showRefresh) setRefreshing(true);
      else setLoading(true);
      setError("");

      const [
        customersResponse,
        machinesResponse,
        billsResponse,
        cycleResponse,
      ] = await Promise.all([
        api.get("/customers/", {
          params: { page: 1, page_size: 100 },
        }),
        api.get("/machines/", {
          params: { page: 1, page_size: 100 },
        }),
        api.get("/rental-bills/", {
          params: { page: 1, page_size: 500 },
        }),
        api.get("/rental-billing-cycle/"),
      ]);

      const customerData = extractArray(
        customersResponse.data,
        ["customers"]
      );
      const machineDataFromApi = extractArray(
        machinesResponse.data,
        ["machines"]
      );

      // Some customer endpoints include the assigned machine details even when
      // the machine list endpoint omits newly-added schema fields. Merge both
      // sources by machine ID so rental billing gets the latest customer rates
      // and per-type free-copy allowances without losing meter values.
      const nestedCustomerMachines = customerData.flatMap((customer) =>
        (Array.isArray(customer?.machines) ? customer.machines : []).map((machine) => ({
          ...machine,
          customer_id: machine?.customer_id ?? customer?.id,
          serial_number: machine?.serial_number ?? machine?.machine_serial_number ?? machine?.machine_serial ?? null,
        }))
      );
      const mergedMachines = new Map();
      machineDataFromApi.forEach((machine) => {
        if (machine?.id != null) mergedMachines.set(Number(machine.id), machine);
      });
      nestedCustomerMachines.forEach((machine) => {
        if (machine?.id == null) return;
        const id = Number(machine.id);
        mergedMachines.set(id, {
          ...(mergedMachines.get(id) || {}),
          ...machine,
          id: machine.id,
          customer_id: machine?.customer_id ?? mergedMachines.get(id)?.customer_id,
        });
      });
      const machineData = Array.from(mergedMachines.values());
      const billData = extractArray(
        billsResponse.data,
        ["bills"]
      );

      const cycleData = cycleResponse?.data || {};
      const serverBillingMonth =
        cycleData?.active_billing_month ||
        cycleData?.activeBillingMonth ||
        getCurrentMonth();

      setActiveBillingMonth(serverBillingMonth);
      setBillingMonth(serverBillingMonth);

      setCustomers(customerData);
      setMachines(machineData);
      setRentalBills(billData);

      setDraftReadings(() => {
        const next = {};

        machineData.forEach((machine) => {
          if (machine?.id == null) return;

          const currentMonthBill = billData.find(
            (bill) =>
              Number(getBillMachineId(bill)) === Number(machine.id) &&
              getBillMonth(bill) === serverBillingMonth
          );

          next[machine.id] = currentMonthBill
            ? String(
                getBillCurrent(
                  currentMonthBill,
                  getMachineReading(machine)
                )
              )
            : "";
        });

        return next;
      });

      setDraftPrices(() => {
        const next = {};

        machineData.forEach((machine) => {
          if (machine?.id != null) {
            next[machine.id] = String(getMachinePrice(machine));
          }
        });

        return next;
      });

      setDraftPaymentStatuses(() => {
        const next = {};

        machineData.forEach((machine) => {
          if (machine?.id == null) return;

          const currentMonthBill = billData.find(
            (bill) =>
              Number(getBillMachineId(bill)) === Number(machine.id) &&
              getBillMonth(bill) === serverBillingMonth
          );

          next[machine.id] = currentMonthBill
            ? getBillStatus(currentMonthBill)
            : "PENDING";
        });

        return next;
      });

      return {
        customers: customerData,
        machines: machineData,
        bills: billData,
      };
    } catch (requestError) {
      console.error("Rental Page Load Error:", requestError);
      setError(
        getApiErrorMessage(
          requestError,
          "Unable to load rental data"
        )
      );
      setCustomers([]);
      setMachines([]);
      setRentalBills([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadRentalData(false);
  }, []);

  // -----------------------------------------------------
  // Add customer from Rental / AMC page
  // Reuses the exact same CustomerForm used by Customers.
  // -----------------------------------------------------
  const handleAddCustomer = (prefillName = "") => {
    const name = String(prefillName || "").trim();

    setPendingNewCustomerName(name);
    setCustomerFormWasOpen(true);
    setSelectedCustomer({
      __create: true,
      prefill_customer_name: name,
    });
  };

  // When the shared CustomerForm closes after saving/cancelling,
  // refresh rental data so newly assigned machines appear here.
  useEffect(() => {
    if (!customerFormWasOpen || customerFormSelection) return;

    let cancelled = false;

    const refreshAfterCustomerSave = async () => {
      setCustomerFormWasOpen(false);

      const refreshed = await loadRentalData(true);

      if (cancelled || !refreshed) return;

      const typedName = pendingNewCustomerName.trim().toLowerCase();

      if (!typedName) {
        setPendingNewCustomerName("");
        return;
      }

      const createdCustomer = refreshed.customers.find((customer) =>
        getCustomerName(customer).trim().toLowerCase() === typedName
      );

      if (createdCustomer?.id != null) {
        selectBillCustomer(createdCustomer);
        toast.success(`${getCustomerName(createdCustomer)} is ready for the rental bill.`);
      }

      setPendingNewCustomerName("");
    };

    refreshAfterCustomerSave();

    return () => {
      cancelled = true;
    };
  }, [customerFormSelection, customerFormWasOpen]);

  const customerMap = useMemo(() => {
    const map = new Map();
    customers.forEach((customer) => {
      if (customer?.id != null) map.set(Number(customer.id), customer);
    });
    return map;
  }, [customers]);

  const billMap = useMemo(() => {
    const map = new Map();
    rentalBills.forEach((bill) => {
      const machineId = getBillMachineId(bill);
      const month = getBillMonth(bill);
      if (machineId != null && month) {
        map.set(`${Number(machineId)}-${month}`, bill);
      }
    });
    return map;
  }, [rentalBills]);

  const rentalRows = useMemo(() => {
    return machines
      .map((machine) => {
        const customerId = Number(machine?.customer_id);
        const customer = customerMap.get(customerId);
        const bill = billMap.get(`${Number(machine?.id)}-${billingMonth}`);

        const customerName = getCustomerName(
          customer || {
            id: customerId,
            customer_name: machine?.customer_name,
          }
        );

        const machineName = getMachineName(machine);
        const machineNumber = getMachineNumber(machine);
        const serialNumber = getMachineSerial(machine);
        const currentReading = getMachineReading(machine);
        const openingReading = getOpeningReading(machine);
        const price = getMachinePrice(machine);
        const hasRollover = Boolean(rolloverDoneForMonth[billingMonth]);

        const previousReading = bill
          ? getBillPrevious(bill, openingReading)
          : currentReading;

        const monthlyReading = bill
          ? getBillCurrent(bill, currentReading)
          : hasRollover
            ? null
            : currentReading;

        const billPrice = bill ? getBillPrice(bill, price) : price;
        const copies = bill
          ? getBillCopies(bill, previousReading, monthlyReading)
          : 0;
        const amount = bill
          ? getBillAmount(bill, copies, billPrice)
          : 0;

        const searchSource = [
          customerName,
          getCustomerCode(customer),
          getCustomerPhone(customer),
          getCustomerEmail(customer),
          getCustomerAddress(customer),
          machineName,
          machineNumber,
          serialNumber,
        ]
          .join(" ")
          .toLowerCase();

        return {
          machine,
          customer,
          customerId,
          customerName,
          customerCode: getCustomerCode(customer),
          customerPhone: getCustomerPhone(customer),
          customerEmail: getCustomerEmail(customer),
          customerAddress: getCustomerAddress(customer),
          machineName,
          machineNumber,
          serialNumber,
          bill,
          currentReading,
          previousReading,
          monthlyReading,
          price,
          billPrice,
          copies,
          amount,
          status: bill ? getBillStatus(bill) : "Pending",
          hasRollover,
          searchSource,
        };
      })
      .filter((row) =>
        appliedSearch.trim()
          ? row.searchSource.includes(appliedSearch.trim().toLowerCase())
          : true
      )
      .sort((a, b) => a.customerName.localeCompare(b.customerName));
  }, [
    machines,
    customerMap,
    billMap,
    billingMonth,
    appliedSearch,
    rolloverDoneForMonth,
  ]);

  const customerGroups = useMemo(() => {
    const map = new Map();

    rentalRows.forEach((row) => {
      if (!map.has(row.customerId)) {
        map.set(row.customerId, {
          customerId: row.customerId,
          customer: row.customer,
          customerName: row.customerName,
          customerCode: row.customerCode,
          customerPhone: row.customerPhone,
          customerEmail: row.customerEmail,
          customerAddress: row.customerAddress,
          machines: [],
        });
      }
      map.get(row.customerId).machines.push(row);
    });

    return Array.from(map.values()).sort((a, b) =>
      a.customerName.localeCompare(b.customerName)
    );
  }, [rentalRows]);

  useEffect(() => {
    if (
      selectedCustomerId != null &&
      !customerGroups.some((group) => group.customerId === selectedCustomerId)
    ) {
      setSelectedCustomerId(null);
      setSelectedMachineId(null);
    }
  }, [customerGroups, selectedCustomerId]);

  const selectedCustomer = useMemo(
    () =>
      customerGroups.find(
        (group) => group.customerId === Number(selectedCustomerId)
      ) || null,
    [customerGroups, selectedCustomerId]
  );

  const selectedMachine = useMemo(
    () =>
      selectedCustomer?.machines.find(
        (row) => Number(row.machine?.id) === Number(selectedMachineId)
      ) ||
      selectedCustomer?.machines?.[0] ||
      null,
    [selectedCustomer, selectedMachineId]
  );

  const selectedMachineHistory = useMemo(() => {
    if (!selectedMachineId) return [];

    const machineId = Number(selectedMachineId);
    const machine = machines.find(
      (item) => Number(item?.id) === machineId
    );

    if (!machine) return [];

    const machineCustomerId = Number(machine?.customer_id);
    const customer = customerMap.get(machineCustomerId);

    return rentalBills
      .filter(
        (bill) => Number(getBillMachineId(bill)) === machineId
      )
      .map((bill) => {
        const previous = getBillPrevious(
          bill,
          getOpeningReading(machine)
        );
        const current = getBillCurrent(
          bill,
          getMachineReading(machine)
        );
        const price = getBillPrice(
          bill,
          getMachinePrice(machine)
        );
        const copies = getBillCopies(
          bill,
          previous,
          current
        );
        const amount = getBillAmount(
          bill,
          copies,
          price
        );

        return {
          id: bill?.id ?? bill?.bill_id,
          month: getBillMonth(bill),
          previous,
          current,
          price,
          copies,
          amount,
          status: getBillStatus(bill),
          customerName: getCustomerName(customer || machine),
          customerCode: getCustomerCode(customer),
          machineName: getMachineName(machine),
          machineNumber: getMachineNumber(machine),
          serialNumber: getMachineSerial(machine),
        };
      })
      .filter((row) => row.month)
      .sort((a, b) => String(b.month).localeCompare(String(a.month)));
  }, [
    selectedMachineId,
    rentalBills,
    machines,
    customerMap,
  ]);

  const selectedHistoryTotals = useMemo(
    () =>
      selectedMachineHistory.reduce(
        (total, row) => ({
          copies: total.copies + Number(row.copies || 0),
          amount: total.amount + Number(row.amount || 0),
        }),
        { copies: 0, amount: 0 }
      ),
    [selectedMachineHistory]
  );

  const filteredRentalRows = useMemo(() => {
    return rentalRows.filter((row) => {
      const status = normalizePaymentStatus(getBillStatus(row.bill || row));
      const paymentMatches =
        paymentFilter === "ALL" || status === paymentFilter;
      const readingMatches =
        readingFilter === "ALL" ||
        (readingFilter === "UPDATED"
          ? isReadingUpdated(row)
          : !isReadingUpdated(row));
      return paymentMatches && readingMatches;
    });
  }, [rentalRows, paymentFilter, readingFilter]);

  const filteredCustomerGroups = useMemo(() => {
    if (!searchText.trim()) return customerGroups;

    return customerGroups
      .map((group) => ({
        ...group,
        machines: group.machines.filter((machineRow) => {
          const status = normalizePaymentStatus(
            getBillStatus(machineRow.bill || machineRow)
          );
          const paymentMatches =
            paymentFilter === "ALL" || status === paymentFilter;
          const readingMatches =
            readingFilter === "ALL" ||
            (readingFilter === "UPDATED"
              ? isReadingUpdated(machineRow)
              : !isReadingUpdated(machineRow));
          return paymentMatches && readingMatches;
        }),
      }))
      .filter((group) => group.machines.length > 0);
  }, [customerGroups, searchText, paymentFilter, readingFilter]);

  const filteredCustomerMachineCount = useMemo(
    () =>
      filteredCustomerGroups.reduce(
        (total, group) => total + group.machines.length,
        0
      ),
    [filteredCustomerGroups]
  );

  const rentalCustomerCount = customerGroups.length;
  const rentalMachineCount = machines.length;

  const monthlyReadingCount = useMemo(
    () => rentalRows.filter((row) => Boolean(row.bill)).length,
    [rentalRows]
  );

  const totalMonthlyAmount = useMemo(
    () => rentalRows.reduce((total, row) => total + Number(row.amount || 0), 0),
    [rentalRows]
  );

  const pendingCount = useMemo(
    () => rentalRows.filter((row) => !row.bill).length,
    [rentalRows]
  );

  const handleSearch = (event) => {
    event.preventDefault();
    setAppliedSearch(searchText);
  };

  const handleSearchChange = (event) => {
    const value = event.target.value;
    setSearchText(value);
    setAppliedSearch(value);
    setSelectedCustomerId(null);
    setSelectedMachineId(null);
  };

  const handleReset = () => {
    setSearchText("");
    setAppliedSearch("");
    setPaymentFilter("ALL");
    setReadingFilter("ALL");
    setBillingMonth(activeBillingMonth || getCurrentMonth());
  };

  const openCustomer = (group) => {
    setSelectedCustomerId(group.customerId);
    setSelectedMachineId(group.machines[0]?.machine?.id ?? null);
  };

  const selectMachine = (machineId) => {
    setSelectedMachineId(machineId);
  };

  const updateDraftReading = (machineId, value) => {
    setDraftReadings((previous) => ({
      ...previous,
      [machineId]: value,
    }));
  };

  const updateDraftPrice = (machineId, value) => {
    setDraftPrices((previous) => ({
      ...previous,
      [machineId]: value,
    }));
  };

  const getNextMonth = (month) => {
    const [year, monthNumber] = String(month).split("-").map(Number);
    if (!year || !monthNumber) return getCurrentMonth();

    const nextDate = new Date(year, monthNumber, 1);
    return `${nextDate.getFullYear()}-${String(
      nextDate.getMonth() + 1
    ).padStart(2, "0")}`;
  };

  const handleStartNewMonth = () => {
    const nextMonth = getNextMonth(billingMonth);
    setRolloverTargetMonth(nextMonth);
    setRolloverModalOpen(true);
  };

  const confirmStartNewMonth = async () => {
    try {
      setRollingOver(true);

      const fallbackNextMonth =
        rolloverTargetMonth ||
        getNextMonth(activeBillingMonth || billingMonth);

      const response = await api.post(
        "/rental-billing-cycle/start"
      );

      const serverNextMonth =
        response?.data?.active_billing_month ||
        response?.data?.activeBillingMonth ||
        fallbackNextMonth;

      setActiveBillingMonth(serverNextMonth);
      setBillingMonth(serverNextMonth);

      const nextDraftReadings = {};

      machines.forEach((machine) => {
        if (machine?.id != null) {
          nextDraftReadings[machine.id] = "";
        }
      });

      setDraftReadings(nextDraftReadings);

      setRolloverDoneForMonth((previous) => ({
        ...previous,
        [serverNextMonth]: true,
      }));

      setRolloverTargetMonth("");
      setRolloverModalOpen(false);

      await loadRentalData(true);

      toast.success(
        `${monthLabel(serverNextMonth)} started successfully. New readings are blank.`
      );
    } catch (requestError) {
      console.error("Start New Month Error:", requestError);

      toast.error(
        getApiErrorMessage(
          requestError,
          "Unable to start the new rental month."
        )
      );
    } finally {
      setRollingOver(false);
    }
  };

  const handleSaveMachine = async (row) => {
    const machineId = row?.machine?.id;
    const customerId = row?.customerId;
    const billId = row?.bill?.id ?? row?.bill?.bill_id;

    if (!machineId || !customerId) {
      toast.error("Customer or machine ID is missing");
      return;
    }

    const previousReading = Number(row.previousReading) || 0;
    const draftReading = draftReadings[machineId] ?? "";
    const newReading = Number(draftReading);
    const newPrice = Number(draftPrices[machineId] ?? row.price);

    const paymentStatus =
      String(
        draftPaymentStatuses[machineId] ??
          row.status ??
          "PENDING"
      )
        .trim()
        .toUpperCase() === "RECEIVED"
        ? "RECEIVED"
        : "PENDING";

    if (
      draftReading === "" ||
      !Number.isInteger(newReading) ||
      newReading < 0
    ) {
      toast.error("Enter a valid new reading");
      return;
    }

    if (newReading < previousReading) {
      toast.error(
        `New reading cannot be less than ${formatNumber(previousReading)}`
      );
      return;
    }

    if (!Number.isFinite(newPrice) || newPrice < 0) {
      toast.error("Enter a valid price per copy");
      return;
    }

    try {
      setSavingMachineId(machineId);

      /*
       * IMPORTANT:
       * Price belongs to the customer's rental machine.
       *
       * Machine.customer_id identifies the particular customer and
       * Machine.cost_per_copy stores that customer's price.
       *
       * Always save the machine price FIRST.
       *
       * The rental-bill create service reads the price directly from
       * machine.cost_per_copy, so sending cost_per_copy only in the
       * rental-bill POST is not enough.
       */
      await api.put(`/machines/${machineId}`, {
        cost_per_copy: newPrice,
      });

      if (!billId) {
        /*
         * New month:
         *
         * 1. Machine price is already updated above.
         * 2. Create the monthly bill.
         * 3. Backend reads the newly saved machine price.
         * 4. Backend stores that price in this month's bill.
         * 5. Backend updates the machine current meter.
         */
        await api.post("/rental-bills/", {
          customer_id: Number(customerId),
          machine_id: Number(machineId),
          billing_month: billingMonth,
          billing_date: `${billingMonth}-01`,
          previous_meter: previousReading,
          current_meter: newReading,
          payment_status: paymentStatus,
          remarks: null,
        });

        toast.success(
          `Price ${formatMoney(newPrice)} and monthly reading saved successfully`
        );
      } else {
        /*
         * Existing month:
         *
         * The machine price has already been updated above.
         * Payment status can be updated on the existing bill.
         *
         * The existing rental-bill backend intentionally does not
         * silently rewrite an already-created meter reading.
         */
        /*
         * Existing monthly bill:
         *
         * Send BOTH the changed reading and changed price to the
         * rental-bill update API.
         *
         * The backend recalculates:
         *   copies_used
         *   total_amount
         *   outstanding_amount
         *
         * and synchronizes the machine's current meter + price.
         *
         * This is important because updating only the machine price
         * would not change the price stored in the existing monthly
         * bill, and the customer portal would continue seeing the
         * old bill price.
         */
        await api.put(`/rental-bills/${billId}`, {
          current_meter: newReading,
          cost_per_copy: newPrice,
          payment_status: paymentStatus,
        });

        toast.success(
          `Reading and price ${formatMoney(newPrice)} updated for ${row.customerName}`
        );
      }

      await loadRentalData(true);
    } catch (requestError) {
      console.error(
        "Rental Reading / Customer Price Save Error:",
        requestError
      );

      toast.error(
        getApiErrorMessage(
          requestError,
          "Failed to update the customer's rental price"
        )
      );
    } finally {
      setSavingMachineId(null);
    }
  };


  const filteredBillCustomers = useMemo(() => {
    const query = billCustomerSearch.trim().toLowerCase();
    if (!query) return customers.slice(0, 50);

    return customers
      .filter((customer) => {
        const values = [
          getCustomerName(customer),
          getCustomerCode(customer),
          getCustomerPhone(customer),
          customer?.email,
          customer?.company_name,
          customer?.name,
        ];

        return values.some((value) =>
          String(value ?? "").toLowerCase().includes(query)
        );
      })
      .slice(0, 50);
  }, [customers, billCustomerSearch]);

  const billCustomer = useMemo(
    () =>
      customers.find(
        (customer) => Number(customer?.id) === Number(billCustomerId)
      ) || null,
    [customers, billCustomerId]
  );

  const billCustomerMachines = useMemo(
    () =>
      machines.filter(
        (machine) =>
          Number(machine?.customer_id) === Number(billCustomerId)
      ),
    [machines, billCustomerId]
  );

  const billMachineRow = useMemo(() => {
    if (!billMachineId) return null;
    const machine = machines.find(
      (item) => Number(item?.id) === Number(billMachineId)
    );
    if (!machine) return null;

    const row = rentalRows.find(
      (item) => Number(item?.machine?.id) === Number(billMachineId)
    );

    return {
      machine,
      row,
    };
  }, [billMachineId, machines, rentalRows]);

  const billCalculation = useMemo(() => {
    if (!billMachineRow?.machine) {
      return calculateRentalBill({ machine: null, readings: {}, gstPercent: billGSTPercent });
    }
    return calculateRentalBill({
      machine: billMachineRow.machine,
      readings: billPrintReadings,
      gstPercent: billGSTPercent,
      previousReadings: editingInvoice?.printPreviousReadings,
    });
  }, [billMachineRow, billPrintReadings, billGSTPercent, editingInvoice]);

  const resetBillForm = () => {
    setEditingInvoice(null);
    setBillCustomerId("");
    setBillCustomerSearch("");
    setBillCustomerSearchOpen(false);
    setBillMachineId("");
    setBillCurrentReading("");
    setBillPrintReadings({ a4_bw: "", a4_color: "", a3_bw: "", a3_color: "" });
    setBillGSTPercent("18");
    setBillBillingMonth(getCurrentMonth());
    setInvoicePreview(null);
  };

  const openCreateRentalBill = () => {
    resetBillForm();
    setBillDrawerOpen(true);
  };

  const openEditRentalBill = (invoice) => {
    const billId = Number(invoice?.serverBillId ?? invoice?.id);
    if (!Number.isInteger(billId) || billId <= 0) {
      toast.error("This bill has no database ID and cannot be edited.");
      return;
    }
    const customer = customers.find((item) => Number(item.id) === Number(invoice.customerId));
    const machine = machines.find((item) => Number(item.id) === Number(invoice.machineId));
    if (!customer || !machine) {
      toast.error("Could not find this bill's customer or machine. Refresh and try again.");
      return;
    }
    const previousReadings = invoice.printPreviousReadings || Object.fromEntries(
      RENTAL_PRINT_TYPES.map((type) => [type.key, getPrintPreviousReading(machine, type.key)])
    );
    const currentReadings = invoice.printReadings || Object.fromEntries(
      RENTAL_PRINT_TYPES.map((type) => [type.key, Number(machine[type.meterKey] || 0)])
    );
    setEditingInvoice({ ...invoice, id: billId, serverBillId: billId, printPreviousReadings: previousReadings, printReadings: currentReadings });
    setBillCustomerId(String(customer.id));
    setBillCustomerSearch(getCustomerName(customer));
    setBillCustomerSearchOpen(false);
    setBillMachineId(String(machine.id));
    setBillPrintReadings(Object.fromEntries(RENTAL_PRINT_TYPES.map((type) => [type.key, String(currentReadings[type.key] ?? "")] )));
    setBillGSTPercent(String(invoice.gstPercent ?? 18));
    setBillBillingMonth(invoice.billingMonth || getCurrentMonth());
    setInvoicePreview(null);
    setBillDrawerOpen(true);
  };

  const handleDeleteRentalBill = async (invoice) => {
    const billId = Number(invoice?.serverBillId ?? invoice?.id);
    if (!Number.isInteger(billId) || billId <= 0) {
      toast.error("This bill has no database ID and cannot be cancelled.");
      return;
    }
    const confirmed = window.confirm(`Cancel rental bill ${invoice.invoiceNumber}? The backend keeps a cancelled bill record for history.`);
    if (!confirmed) return;
    try {
      setDeletingBillId(billId);
      await api.delete(`/rental-bills/${billId}`);
      setGeneratedInvoices((items) => items.filter((item) => Number(item.serverBillId ?? item.id) !== billId));
      await loadRentalData(true);
      toast.success(`Rental bill ${invoice.invoiceNumber} cancelled.`);
    } catch (deleteError) {
      console.error("Rental bill cancellation failed:", deleteError, deleteError?.response?.data);
      toast.error(getApiErrorMessage(deleteError, "Could not cancel this rental bill."));
    } finally {
      setDeletingBillId(null);
    }
  };

  const closeCreateRentalBill = () => {
    if (generatingInvoice) return;
    setBillDrawerOpen(false);
    resetBillForm();
  };

  const selectBillCustomer = (customer) => {
    if (!customer?.id) return;

    const customerId = String(customer.id);
    setBillCustomerId(customerId);
    setBillCustomerSearch(getCustomerName(customer));
    setBillCustomerSearchOpen(false);
    setInvoicePreview(null);

    const assignedMachines = machines.filter(
      (machine) => Number(machine?.customer_id) === Number(customerId)
    );
    const firstMachine = assignedMachines[0];

    setBillMachineId(firstMachine?.id ? String(firstMachine.id) : "");
    setBillCurrentReading("");
    setBillPrintReadings(firstMachine ? {
      a4_bw: String(getPrintPreviousReading(firstMachine, "a4_bw")),
      a4_color: String(getPrintPreviousReading(firstMachine, "a4_color")),
      a3_bw: String(getPrintPreviousReading(firstMachine, "a3_bw")),
      a3_color: String(getPrintPreviousReading(firstMachine, "a3_color")),
    } : { a4_bw: "", a4_color: "", a3_bw: "", a3_color: "" });
  };

  const handleBillCustomerSearchChange = (event) => {
    setBillCustomerSearch(event.target.value);
    setBillCustomerId("");
    setBillMachineId("");
    setBillCurrentReading("");
    setBillCustomerSearchOpen(true);
  };

  const handleBillCustomerChange = (event) => {
    const customerId = event.target.value;
    const customer = customers.find(
      (item) => Number(item?.id) === Number(customerId)
    );
    if (customer) selectBillCustomer(customer);
  };

  const handleBillMachineChange = (event) => {
    const machineId = event.target.value;
    setBillMachineId(machineId);
    setInvoicePreview(null);
    const machine = machines.find((item) => Number(item?.id) === Number(machineId));
    setBillCurrentReading("");
    setBillPrintReadings(machine ? {
      a4_bw: String(getPrintPreviousReading(machine, "a4_bw")),
      a4_color: String(getPrintPreviousReading(machine, "a4_color")),
      a3_bw: String(getPrintPreviousReading(machine, "a3_bw")),
      a3_color: String(getPrintPreviousReading(machine, "a3_color")),
    } : { a4_bw: "", a4_color: "", a3_bw: "", a3_color: "" });
  };

  const buildInvoiceData = () => {
    const machine = billMachineRow?.machine;
    if (!billCustomer || !machine) return null;

    for (const type of RENTAL_PRINT_TYPES) {
      const previous = editingInvoice?.printPreviousReadings?.[type.key] != null
        ? Number(editingInvoice.printPreviousReadings[type.key])
        : getPrintPreviousReading(machine, type.key);
      const raw = billPrintReadings[type.key];
      if (raw === "" || raw == null || !Number.isFinite(Number(raw)) || Number(raw) < previous) {
        toast.error(`${type.label}: enter a reading greater than or equal to ${formatNumber(previous)}`);
        return null;
      }
    }

    const calculation = calculateRentalBill({
      machine,
      readings: billPrintReadings,
      gstPercent: billGSTPercent,
      previousReadings: editingInvoice?.printPreviousReadings,
    });

    return {
      id: editingInvoice?.serverBillId ?? `local-${Date.now()}`,
      serverBillId: editingInvoice?.serverBillId ?? null,
      billingMonth: billBillingMonth || getCurrentMonth(),
      billingDate: formatDateISO(new Date()),
      dueDate: addDaysToDate(formatDateISO(new Date()), 15),
      invoiceNumber: editingInvoice?.invoiceNumber || makeInvoiceNumber(billBillingMonth || getCurrentMonth(), generatedInvoices.length + 1, formatDateISO(new Date())),
      customerId: Number(billCustomer.id),
      customerName: getCustomerName(billCustomer),
      customerCode: getCustomerCode(billCustomer),
      customerPhone: getCustomerPhone(billCustomer),
      customerEmail: getCustomerEmail(billCustomer),
      customerAddress: getCustomerAddress(billCustomer),
      gstin: getCustomerGSTIN(billCustomer),
      machineId: Number(machine.id),
      machineName: getMachineName(machine),
      machineNumber: getMachineNumber(machine),
      serialNumber: getMachineSerial(machine),
      printReadings: { ...billPrintReadings },
      printRates: {
        a4_bw: getMachineA4BWRate(machine),
        a4_color: getMachineA4ColorRate(machine),
        a3_bw: getMachineA3BWRate(machine),
        a3_color: getMachineA3ColorRate(machine),
      },
      rentalAmount: calculation.fixedRent,
      freeCopyAllowance: calculation.freeAllowance,
      ...calculation,
      status: "PENDING",
      createdAt: new Date().toISOString(),
    };
  };

  const handleGenerateInvoice = async () => {
    try {
      setGeneratingInvoice(true);

      const invoice = buildInvoiceData();
      if (!invoice) return;

      // Persist the bill through the backend API before showing success.
      // This requires the updated RentalBillCreate schema and service.
      const payload = {
        customer_id: invoice.customerId,
        machine_id: invoice.machineId,
        billing_month: invoice.billingMonth,
        // Backend requires billing_date to fall within billing_month.
        // Keep invoice.billingDate for the actual generated-on display, but
        // send the first day of the selected billing month to this field.
        billing_date: `${invoice.billingMonth}-01`,
        due_date: invoice.dueDate,
        bill_number: invoice.invoiceNumber,
        gst_rate: Number(invoice.gstPercent),
        billing_mode: "FOUR_TYPE",
        a4_bw_current_meter: invoice.printBreakdown.find((item) => item.key === "a4_bw")?.current ?? 0,
        a4_color_current_meter: invoice.printBreakdown.find((item) => item.key === "a4_color")?.current ?? 0,
        a3_bw_current_meter: invoice.printBreakdown.find((item) => item.key === "a3_bw")?.current ?? 0,
        a3_color_current_meter: invoice.printBreakdown.find((item) => item.key === "a3_color")?.current ?? 0,
        payment_status: "PENDING",
        remarks: null,
      };

      const customerId = Number(invoice.customerId);
      if (!Number.isInteger(customerId) || customerId <= 0) {
        throw new Error("Please select a valid customer before saving the rental bill.");
      }

      // This backend endpoint requires customer_id in the query string,
      // even though customer_id is also included in the request body.
      const response = editingInvoice
        ? await api.put(`/rental-bills/${Number(editingInvoice.serverBillId ?? editingInvoice.id)}`, {
            billing_month: invoice.billingMonth,
            billing_date: `${invoice.billingMonth}-01`,
            gst_rate: Number(invoice.gstPercent),
            billing_mode: "FOUR_TYPE",
            a4_bw_current_meter: Number(payload.a4_bw_current_meter),
            a4_color_current_meter: Number(payload.a4_color_current_meter),
            a3_bw_current_meter: Number(payload.a3_bw_current_meter),
            a3_color_current_meter: Number(payload.a3_color_current_meter),
          })
        : await api.post("/rental-bills/", payload, {
            params: { customer_id: customerId },
          });

      // APIs may return the bill directly or wrap it in { data }, { bill },
      // or { success, data: { bill } }. Unwrap those shapes before reading ID.
      const responseBody = response?.data ?? {};
      const savedBill =
        responseBody?.data?.bill ??
        responseBody?.bill ??
        responseBody?.data?.data?.bill ??
        responseBody?.data?.data ??
        responseBody?.data ??
        responseBody;
      const savedBillId = Number(
        savedBill?.id ?? savedBill?.bill_id ?? savedBill?.rental_bill_id ??
        (editingInvoice ? editingInvoice.serverBillId ?? editingInvoice.id : NaN)
      );

      // Never silently keep a local-only ID: the PDF upload needs the real
      // primary key returned by PostgreSQL.
      if (!Number.isInteger(savedBillId) || savedBillId <= 0) {
        console.error("Rental bill create response did not include a database ID:", responseBody);
        throw new Error(
          "The rental bill API did not return a database bill ID. Check the POST /rental-bills/ response in DevTools → Network."
        );
      }

      if (editingInvoice) {
        // Rebuild the server-side PDF so it reflects the corrected readings.
        await api.post(`/rental-bills/${savedBillId}/generate-pdf`);
      }

      // Carry this bill's final readings forward as the machine's next
      // previous readings. Persist the four separate counters so the next
      // bill starts from these values rather than zero or an older reading.
      // The machine schema/API must allow these four fields to be updated.
      try {
        await api.put(`/machines/${invoice.machineId}`, {
          a4_bw_current_meter: Number(payload.a4_bw_current_meter),
          a4_color_current_meter: Number(payload.a4_color_current_meter),
          a3_bw_current_meter: Number(payload.a3_bw_current_meter),
          a3_color_current_meter: Number(payload.a3_color_current_meter),
        });
      } catch (meterUpdateError) {
        console.error("Bill saved, but machine readings could not be rolled forward:", meterUpdateError);
        toast.error("Bill was saved, but machine readings were not updated. Check the machine update API.");
      }

      // The backend is the source of truth for persisted billing totals.
      // Use its saved readings, per-type charges, rental, GST, and grand total
      // in the invoice preview so the PDF matches the database record.
      const savedPrintBreakdown = RENTAL_PRINT_TYPES.map((type) => ({
        ...type,
        label: type.label,
        previous: Number(savedBill[`${type.key}_previous_meter`] ?? invoice.printBreakdown.find((item) => item.key === type.key)?.previous ?? 0),
        current: Number(savedBill[`${type.key}_current_meter`] ?? invoice.printBreakdown.find((item) => item.key === type.key)?.current ?? 0),
        copies: Number(savedBill[`${type.key}_copies_used`] ?? invoice.printBreakdown.find((item) => item.key === type.key)?.copies ?? 0),
        freeCopies: Number(savedBill[`${type.key}_free_copies`] ?? invoice.printBreakdown.find((item) => item.key === type.key)?.freeCopies ?? 0),
        chargeableCopies: Math.max(
          Number(savedBill[`${type.key}_copies_used`] ?? invoice.printBreakdown.find((item) => item.key === type.key)?.copies ?? 0) -
          Number(savedBill[`${type.key}_free_copies`] ?? invoice.printBreakdown.find((item) => item.key === type.key)?.freeCopies ?? 0),
          0
        ),
        rate: Number(savedBill[`${type.key}_rate`] ?? invoice.printBreakdown.find((item) => item.key === type.key)?.rate ?? 0),
        amount: Number(savedBill[`${type.key}_amount`] ?? invoice.printBreakdown.find((item) => item.key === type.key)?.amount ?? 0),
      }));
      const savedSubtotal = Number(savedBill.subtotal_amount ?? invoice.subtotal);
      const savedGstAmount = Number(savedBill.gst_amount ?? invoice.gstAmount);
      const savedGrandTotal = Number(savedBill.total_amount ?? invoice.grandTotal);
      const savedInvoice = {
        ...invoice,
        id: savedBillId,
        serverBillId: savedBillId,
        invoiceNumber: savedBill.bill_number ?? savedBill.invoice_number ?? invoice.invoiceNumber,
        status: savedBill.payment_status ?? invoice.status,
        printBreakdown: savedPrintBreakdown,
        printReadings: Object.fromEntries(savedPrintBreakdown.map((item) => [item.key, item.current])),
        printPreviousReadings: Object.fromEntries(savedPrintBreakdown.map((item) => [item.key, item.previous])),
        previousReading: Number(savedBill.previous_meter ?? invoice.previousReading),
        currentReading: Number(savedBill.current_meter ?? invoice.currentReading),
        usedCopies: Number(savedBill.copies_used ?? invoice.usedCopies),
        freeCopies: Number(savedBill.free_copies_applied ?? invoice.freeCopies),
        freeAllowance: Number(savedBill.free_copy_allowance ?? invoice.freeAllowance),
        fixedRent: Number(savedBill.rental_amount ?? invoice.fixedRent),
        copyCharges: Number(savedBill.copy_charges_amount ?? invoice.copyCharges),
        subtotal: savedSubtotal,
        gstPercent: Number(savedBill.gst_rate ?? invoice.gstPercent),
        gstAmount: savedGstAmount,
        grandTotal: savedGrandTotal,
        chargeableCopies: savedPrintBreakdown.reduce((sum, item) => sum + item.chargeableCopies, 0),
        backendSaved: true,
      };

      // After a successful save, roll the entered meter values forward:
      // they are now the previous readings for the next bill. Keep the
      // new-reading inputs at those same cumulative meter values so the
      // next bill starts with zero copies used (do NOT reset physical meter
      // readings to numeric zero).
      setBillPrintReadings({
        a4_bw: String(payload.a4_bw_current_meter),
        a4_color: String(payload.a4_color_current_meter),
        a3_bw: String(payload.a3_bw_current_meter),
        a3_color: String(payload.a3_color_current_meter),
      });

      if (editingInvoice) {
        setGeneratedInvoices((previous) => [savedInvoice, ...previous.filter((item) => Number(item.serverBillId ?? item.id) !== savedBillId)]);
        toast.success(`${savedInvoice.invoiceNumber} updated successfully.`);
        setEditingInvoice(null);
      } else {
        setGeneratedInvoices((previous) => [savedInvoice, ...previous]);
        toast.success(`${savedInvoice.invoiceNumber} saved successfully. Meter readings are ready for the next bill.`);
      }
      setInvoicePreview(savedInvoice);
      await loadRentalData(true);
    } catch (error) {
      console.error("Rental bill save failed:", error, error?.response?.data);
      toast.error(
        getApiErrorMessage(
          error,
          "Could not save the rental bill. Check the backend log and rental-bill service."
        )
      );
    } finally {
      setGeneratingInvoice(false);
    }
  };

  const printRentalInvoice = async (invoice) => {
    if (!invoice) return;
    const popup = window.open("", "_blank", "width=1000,height=1000");
    if (!popup) {
      toast.error("Please allow pop-ups to download or print the rental invoice.");
      return;
    }
    const money = (value) => formatMoney(value);
    const escapeHtml = (value) => String(value ?? "—").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
    const displayDate = (value) => {
      if (!value) return "—";
      const date = new Date(`${String(value).slice(0, 10)}T12:00:00`);
      return Number.isNaN(date.getTime()) ? escapeHtml(value) : date.toLocaleDateString("en-IN", { day: "2-digit", month: "2-digit", year: "numeric" });
    };
    const dueDate = invoice.dueDate || addDaysToDate(invoice.billingDate, 15);
    const rows = (invoice.printBreakdown || []).map((item, index) => `
      <tr>
        <td class="center">${index + 1}</td><td>${escapeHtml(item.label)}</td>
        <td class="num">${formatNumber(item.previous)}</td>
        <td class="num">${formatNumber(item.current)}</td>
        <td class="num">${formatNumber(item.copies)}</td><td class="num">${formatNumber(item.freeCopies)}</td>
        <td class="num">${formatNumber(item.chargeableCopies)}</td><td class="num">${money(item.rate)}</td><td class="num">${money(item.amount)}</td>
      </tr>`).join("");

    popup.document.open();
    popup.document.write(`<!doctype html>
      <html><head><meta charset="utf-8"/><title>${escapeHtml(invoice.invoiceNumber)}</title>
      <style>
        *{box-sizing:border-box} body{margin:0;background:#fff;color:#111;font:12px Arial,Helvetica,sans-serif}
        .page{max-width:980px;margin:0 auto;padding:24px 26px;border:1px solid #777;min-height:calc(100vh - 18px)}
        .title{text-align:center;font-size:18px;font-weight:800;margin-bottom:12px}
        .header{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:4px 2px 12px;border-bottom:1px solid #bbb}
        .company h1{font-size:20px;margin:0 0 7px}.company p,.invoice-meta p{margin:4px 0;line-height:1.35}
        .invoice-meta{text-align:right}.invoice-meta h2{font-size:18px;margin:0 0 8px}
        .machine-strip{display:flex;justify-content:space-between;gap:14px;background:#f2f2f2;border:0;border-bottom:1px solid #bbb;padding:9px 2px;margin-top:8px;font-size:12px}
        .parties{display:grid;grid-template-columns:1fr 1fr;border:0;border-bottom:1px solid #bbb;margin-top:8px}
        .party{padding:10px 8px;min-height:105px}.party:first-child{border-right:1px solid #bbb}.party:last-child{border-right:0}
        .bar{background:#aaa;color:#fff;font-weight:800;padding:6px 8px;margin:-10px -10px 8px}
        table{width:100%;border-collapse:collapse;margin-top:10px}th,td{border:1px solid #888;padding:5px 4px;vertical-align:top;font-size:11px}
        th{background:#aaa;color:#fff;text-align:left}.num{text-align:right;white-space:nowrap}.center{text-align:center}
        .summary{width:58%;margin-left:auto;margin-top:10px}.summary td:first-child{width:65%}.summary td:last-child{text-align:right}
        .totals{width:58%;margin:12px 0 0 auto}.totals div{display:flex;justify-content:space-between;padding:5px 8px;border-bottom:1px solid #ccc}
        .totals .grand{font-size:17px;font-weight:800;border-top:2px solid #222;border-bottom:0;margin-top:5px;padding-top:10px}
        .words{margin-top:12px;border:0;border-top:1px solid #bbb;border-bottom:1px solid #bbb;padding:9px 2px}.footer{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:36px;align-items:end}
        .signature{text-align:right;min-height:90px;display:flex;flex-direction:column;justify-content:space-between;align-items:flex-end}
        .signature-line{border-top:1px solid #222;width:220px;text-align:center;padding-top:6px;margin-top:48px}
        .terms{font-size:10px;color:#444;margin-top:14px}
        .toolbar{display:flex;justify-content:flex-end;gap:10px;margin:0 auto 12px;max-width:980px;padding:10px 26px 0}
        button{border:0;border-radius:6px;padding:10px 16px;font-weight:700;cursor:pointer;background:#087f3e;color:white}button.secondary{background:#344054}
        @page{size:A4;margin:8mm}
        @media print{.toolbar{display:none}.page{padding:8mm 6mm;max-width:none;min-height:0;border:1px solid #777;margin:0;break-inside:avoid}}
      </style></head><body>
      <div class="toolbar"><button class="secondary" onclick="window.close()">Close</button><button onclick="window.print()">Download / Save as PDF</button></div>
      <main class="page">
        <div class="title">TAX INVOICE — RENTAL</div>
        <section class="header">
          <div class="company"><h1>DIGITECH IMAGING SOLUTIONS</h1>
            <p>No.1676, 2nd Cross, 14th Main, Prakash Nagar, Bangalore, Karnataka - 560 021</p>
            <p>Phone: 080-41440252 · Email: info@digitechimaging.com</p>
            <p><strong>GSTIN:</strong> 29BQLPS2976R1ZG · <strong>State:</strong> 29-Karnataka</p>
          </div>
          <div class="invoice-meta"><h2>${escapeHtml(invoice.invoiceNumber)}</h2>
            <p><strong>Billing Month:</strong> ${escapeHtml(monthLabel(invoice.billingMonth))}</p>
            <p><strong>Invoice Date:</strong> ${displayDate(invoice.billingDate)}</p>
            <p><strong>Due Date:</strong> ${displayDate(dueDate)} (15 days)</p>
          </div>
        </section>
        <section class="machine-strip"><span><strong>Machine:</strong> ${escapeHtml(invoice.machineName)}</span><span><strong>Serial No.:</strong> ${escapeHtml(invoice.serialNumber)}</span></section>
        <section class="parties">
          <div class="party"><div class="bar">BILL TO</div><strong>${escapeHtml(invoice.customerName)}</strong>
            <p>${escapeHtml(invoice.customerAddress)}</p><p>Phone: ${escapeHtml(invoice.customerPhone || "—")}</p>
            <p>GSTIN: ${escapeHtml(invoice.gstin || "—")}</p>
          </div>
          <div class="party"><div class="bar">INVOICE DETAILS</div><p><strong>Invoice No.:</strong> ${escapeHtml(invoice.invoiceNumber)}</p>
            <p><strong>Date:</strong> ${displayDate(invoice.billingDate)}</p><p><strong>Due Date:</strong> ${displayDate(dueDate)}</p>
            <p><strong>Machine Serial:</strong> ${escapeHtml(invoice.serialNumber)}</p>
          </div>
        </section>
        <table><thead><tr><th>#</th><th>Print Type</th><th>Previous Reading</th><th>Current Reading</th><th>Copies Used</th><th>Free Copies</th><th>Chargeable</th><th>Rate / Copy</th><th>Amount</th></tr></thead><tbody>${rows}</tbody></table>
        <table class="summary"><tbody>
          <tr><td>Fixed Rental</td><td>${money(invoice.fixedRent)}</td></tr>
          <tr><td>Total Free Copies Applied</td><td>${formatNumber(invoice.freeCopies)}</td></tr>
          <tr><td>Total Chargeable Copies</td><td>${formatNumber(invoice.chargeableCopies)}</td></tr>
          <tr><td>Copy Charges (Chargeable Copies × Rate)</td><td>${money(invoice.copyCharges)}</td></tr>
        </tbody></table>
        <div class="totals"><div><span>Subtotal (Fixed Rental + Copy Charges)</span><strong>${money(invoice.subtotal)}</strong></div>
          <div><span>GST (${escapeHtml(invoice.gstPercent)}%)</span><strong>${money(invoice.gstAmount)}</strong></div>
          <div class="grand"><span>GRAND TOTAL</span><strong>${money(invoice.grandTotal)}</strong></div>
        </div>
        <div class="words"><strong>Amount payable:</strong> ${money(invoice.grandTotal)} (Rupees amount as shown above)</div>
        <div class="footer"><div><strong>Terms &amp; Conditions</strong><p>Payment is due within 15 days from the invoice date.</p><p>Please mention the invoice number when making payment.</p></div>
          <div class="signature"><strong>For DIGITECH IMAGING SOLUTIONS</strong><div class="signature-line">Authorized Signature</div></div>
        </div>
      </main></body></html>`);
    popup.document.close();

    // Generate a real PDF Blob from the invoice HTML and persist it in PostgreSQL.
    // The backend route expects multipart/form-data field name "file".
    try {
      const invoiceElement = popup.document.querySelector(".page");
      if (!invoiceElement) {
        throw new Error("Invoice content could not be found for PDF generation.");
      }

      const pdfBlob = await html2pdf()
        .set({
          margin: [8, 6, 8, 6],
          filename: `${invoice.invoiceNumber || "rental-bill"}.pdf`,
          image: { type: "jpeg", quality: 0.98 },
          html2canvas: { scale: 2, useCORS: true, backgroundColor: "#ffffff" },
          jsPDF: { unit: "mm", format: "a4", orientation: "portrait" },
          pagebreak: { mode: ["css", "legacy"] },
        })
        .from(invoiceElement)
        .outputPdf("blob");

      if (!(pdfBlob instanceof Blob) || pdfBlob.size === 0) {
        throw new Error("PDF generation returned an empty file.");
      }

      const savedBillId = Number(invoice.id);
      if (!Number.isInteger(savedBillId) || savedBillId <= 0 || String(invoice.id).startsWith("local-")) {
        throw new Error("This invoice has no database bill ID. Save the bill first, then generate its PDF.");
      }

      const pdfFile = new File(
        [pdfBlob],
        `${invoice.invoiceNumber || `rental-bill-${savedBillId}`}.pdf`,
        { type: "application/pdf" }
      );
      const formData = new FormData();
      formData.append("file", pdfFile);

      // This endpoint requires multipart/form-data. Override any shared Axios
      // JSON defaults and pass FormData through unchanged so the browser/Axios
      // can supply the multipart boundary correctly.
      const uploadResponse = await api.post(
        `/rental-bills/${savedBillId}/pdf`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          transformRequest: [(data) => data],
        }
      );

      const uploadBody = uploadResponse?.data ?? {};
      const uploadData = uploadBody?.data ?? uploadBody;
      const returnedSize = Number(
        uploadData?.pdf_size_bytes ?? uploadData?.size_bytes ?? pdfBlob.size
      );
      if (
        uploadResponse.status < 200 ||
        uploadResponse.status >= 300 ||
        uploadBody?.success === false ||
        uploadData?.success === false
      ) {
        throw new Error(
          uploadData?.message || uploadBody?.message || "The server did not confirm that the PDF was saved."
        );
      }

      toast.success(
        `PDF upload request succeeded (${formatNumber(returnedSize)} bytes). Verify storage in PostgreSQL.`
      );
      // Keep the generated PDF window open so the user can print or save a local copy too.
      popup.focus();
    } catch (pdfError) {
      console.error("Rental bill PDF generation/upload failed:", pdfError);
      toast.error(getApiErrorMessage(pdfError, "Bill exists, but its PDF could not be saved to the database."));
    }
  };

  const invoiceRows = useMemo(() => {
    const localRows = [...generatedInvoices];

    const serverRows = rentalBills
      .filter((bill) => (bill?.id || bill?.bill_id) && String(bill?.payment_status ?? "").toUpperCase() !== "CANCELLED")
      .map((bill) => {
        const machine = machines.find(
          (item) => Number(item?.id) === Number(getBillMachineId(bill))
        );
        const customer = customers.find(
          (item) => Number(item?.id) === Number(machine?.customer_id ?? bill?.customer_id)
        );

        const previous = getBillPrevious(
          bill,
          getOpeningReading(machine)
        );
        const current = getBillCurrent(
          bill,
          getMachineReading(machine)
        );
        const copies = getBillCopies(bill, previous, current);
        const rate = getBillPrice(bill, getMachineExtraRate(machine));
        const fixedRent = Number(
          bill?.fixed_rental_amount ??
            bill?.fixed_rent ??
            getMachineFixedRent(machine)
        ) || 0;
        const freeCopies = Number(
          bill?.free_copies ??
            bill?.free_prints ??
            getMachineFreeCopies(machine)
        ) || 0;
        const chargeableCopies = Math.max(copies - freeCopies, 0);
        const copyCharges = chargeableCopies * rate;
        const subtotal =
          Number(
            bill?.subtotal ??
              bill?.sub_total ??
              bill?.subTotal
          ) || fixedRent + copyCharges;
        const gstPercent = Number(
          bill?.gst_percentage ??
            bill?.gstPercent ??
            bill?.gst_rate ??
            0
        ) || 0;
        const gstAmount =
          Number(bill?.gst_amount ?? bill?.gstAmount) ||
          subtotal * (gstPercent / 100);
        const grandTotal =
          Number(
            bill?.grand_total ??
              bill?.grandTotal ??
              bill?.total_amount
          ) || subtotal + gstAmount;

        return {
          // Keep the real PostgreSQL primary key numeric. The PDF upload
          // endpoint needs this ID; a synthetic "server-31" ID will fail.
          id: Number(bill.id ?? bill.bill_id),
          serverBillId: Number(bill.id ?? bill.bill_id),
          invoiceNumber: firstValue(
            bill?.invoice_number,
            bill?.bill_number,
            `RB-${getBillMonth(bill)}-${bill?.id ?? bill?.bill_id}`
          ),
          billingMonth: getBillMonth(bill),
          billingDate: firstValue(
            bill?.billing_date,
            bill?.bill_date,
            ""
          ),
          customerId: customer?.id ?? bill?.customer_id,
          customerName: getCustomerName(customer || machine),
          machineId: machine?.id ?? getBillMachineId(bill),
          machineName: getMachineName(machine || bill),
          serialNumber: getMachineSerial(machine || bill),
          previousReading: previous,
          currentReading: current,
          printReadings: Object.fromEntries(RENTAL_PRINT_TYPES.map((type) => [
            type.key,
            Number(bill?.[`${type.key}_current_meter`] ?? machine?.[type.meterKey] ?? current ?? 0),
          ])),
          printPreviousReadings: Object.fromEntries(RENTAL_PRINT_TYPES.map((type) => [
            type.key,
            Number(bill?.[`${type.key}_previous_meter`] ?? machine?.[type.meterKey] ?? 0),
          ])),
          printBreakdown: RENTAL_PRINT_TYPES.map((type) => {
            const typePrevious = Number(bill?.[`${type.key}_previous_meter`] ?? machine?.[type.meterKey] ?? 0);
            const typeCurrent = Number(bill?.[`${type.key}_current_meter`] ?? machine?.[type.meterKey] ?? 0);
            const typeCopies = Number(bill?.[`${type.key}_copies_used`] ?? Math.max(typeCurrent - typePrevious, 0));
            const typeFree = Number(bill?.[`${type.key}_free_copies`] ?? 0);
            const typeRate = Number(bill?.[`${type.key}_rate`] ?? machine?.[type.rateKey] ?? 0);
            const typeAmount = Number(bill?.[`${type.key}_amount`] ?? Math.max(typeCopies - typeFree, 0) * typeRate);
            return { ...type, previous: typePrevious, current: typeCurrent, copies: typeCopies, freeCopies: typeFree, chargeableCopies: Math.max(typeCopies - typeFree, 0), rate: typeRate, amount: typeAmount };
          }),
          usedCopies: copies,
          freeCopies,
          chargeableCopies,
          fixedRent,
          extraRate: rate,
          copyCharges,
          subtotal,
          gstPercent,
          gstAmount,
          grandTotal,
          status: normalizePaymentStatus(getBillStatus(bill)),
          serverBill: true,
          invoiceUrl: firstValue(
            bill?.invoice_url,
            bill?.pdf_url,
            bill?.invoice_pdf_url
          ),
        };
      });

    // Prefer local generated records over a duplicate server record.
    const serverKeys = new Set(
      serverRows.map(
        (row) => `${row.machineId}-${row.billingMonth}`
      )
    );

    return [
      ...localRows,
      ...serverRows.filter(
        (row) =>
          !generatedInvoices.some(
            (local) =>
              Number(local.machineId) === Number(row.machineId) &&
              String(local.billingMonth) === String(row.billingMonth)
          )
      ),
    ].sort((a, b) =>
      String(b.billingMonth).localeCompare(String(a.billingMonth))
    );
  }, [generatedInvoices, rentalBills, machines, customers]);

  const filteredInvoiceRows = useMemo(() => {
    const query = invoiceSearchText.trim().toLowerCase();
    if (!query) return invoiceRows;

    return invoiceRows.filter((invoice) => {
      const searchableValues = [
        invoice.invoiceNumber,
        invoice.customerName,
        invoice.machineName,
        invoice.serialNumber,
        invoice.billingMonth,
        monthLabel(invoice.billingMonth),
        invoice.previousReading,
        invoice.currentReading,
        invoice.chargeableCopies,
        invoice.grandTotal,
        formatMoney(invoice.grandTotal),
      ];
      return searchableValues.some((value) =>
        String(value ?? "").toLowerCase().includes(query)
      );
    });
  }, [invoiceRows, invoiceSearchText]);

  // Render invoices in batches and reveal more as the table is scrolled.
  useEffect(() => {
    setVisibleInvoiceCount(25);
  }, [invoiceSearchText, invoiceRows.length]);

  const visibleInvoiceRows = useMemo(
    () => filteredInvoiceRows.slice(0, visibleInvoiceCount),
    [filteredInvoiceRows, visibleInvoiceCount]
  );

  const handleInvoiceTableScroll = (event) => {
    const element = event.currentTarget;
    const closeToBottom = element.scrollTop + element.clientHeight >= element.scrollHeight - 80;
    if (closeToBottom && visibleInvoiceCount < filteredInvoiceRows.length) {
      setVisibleInvoiceCount((count) => Math.min(count + 25, filteredInvoiceRows.length));
    }
  };

  const renderStatus = (row) => {
    const submitted = Boolean(row.bill);
    return (
      <span className={`rental-status ${submitted ? "submitted" : "pending"}`}>
        {submitted ? <CheckCircle2 size={13} /> : <Clock3 size={13} />}
        {submitted ? "Submitted" : "Pending"}
      </span>
    );
  };

  return (
    <div className="rental-layout">
      <Sidebar />

      <main className="rental-page rental-page-shell">
        <Navbar />

        <header className="rental-header">
          <div>
            <div className="rental-title-row">
              <div className="rental-title-icon">
                <Printer size={20} />
              </div>
              <div>
                <h1>Rental Management</h1>
                <p>
                  Manage rental customers, machines and monthly meter readings.
                </p>
              </div>
            </div>
          </div>

          <div className="rental-header-actions">
            <button
              type="button"
              className="refresh-btn"
              onClick={() => loadRentalData(true)}
              disabled={loading || refreshing}
            >
              <RefreshCw size={15} className={refreshing ? "spin" : ""} />
              {refreshing ? "Refreshing" : "Refresh"}
            </button>

            <button
              type="button"
              className="create-rental-bill-btn rental-add-customer-btn"
              onClick={handleAddCustomer}
              disabled={loading || refreshing}
            >
              <Plus size={16} />
              Add Customer
            </button>

            <button
              type="button"
              className="create-rental-bill-btn"
              onClick={openCreateRentalBill}
              disabled={loading || refreshing}
            >
              <Plus size={16} />
              Create New Rental Bill
            </button>

            <button
              type="button"
              className="start-month-btn"
              onClick={handleStartNewMonth}
              disabled={loading || refreshing || rollingOver}
            >
              <RotateCcw size={15} />
              Start New Month
            </button>
          </div>
        </header>

        <section className="rental-summary-grid">
          <div className="rental-summary-card">
            <div className="summary-icon"><Users size={19} /></div>
            <div>
              <span>Rental Customers</span>
              <strong>{rentalCustomerCount}</strong>
            </div>
          </div>

          <div className="rental-summary-card">
            <div className="summary-icon"><Printer size={19} /></div>
            <div>
              <span>Rental Machines</span>
              <strong>{rentalMachineCount}</strong>
            </div>
          </div>

          <div className="rental-summary-card">
            <div className="summary-icon"><CalendarDays size={19} /></div>
            <div>
              <span>{monthLabel(billingMonth)} Submitted</span>
              <strong>{monthlyReadingCount}</strong>
            </div>
          </div>

          <div className="rental-summary-card amount-card">
            <div className="summary-icon"><IndianRupee size={19} /></div>
            <div>
              <span>{monthLabel(billingMonth)} Amount</span>
              <strong>{formatMoney(totalMonthlyAmount)}</strong>
            </div>
          </div>
        </section>

        {error && (
          <div className="rental-error">
            <AlertTriangle size={17} />
            <div>
              <strong>Unable to load rental data</strong>
              <span>{error}</span>
            </div>
            <button type="button" onClick={() => loadRentalData(true)}>
              Try Again
            </button>
          </div>
        )}


        <div className="rental-main-tabs" role="tablist" aria-label="Rental management sections">
            <button
                type="button"
                className={`rental-main-tab ${activeRentalTab === "invoices" ? "active" : ""}`}
                onClick={() => setActiveRentalTab("invoices")}
                role="tab"
                aria-selected={activeRentalTab === "invoices"}
            >
                <span>Rental Bills & Invoices</span>
                <small>Generated monthly invoices</small>
            </button>

            <button
                type="button"
                className={`rental-main-tab ${activeRentalTab === "readings" ? "active" : ""}`}
                onClick={() => setActiveRentalTab("readings")}
                role="tab"
                aria-selected={activeRentalTab === "readings"}
            >
                <span>Monthly Readings</span>
                <small>Meter readings & updates</small>
            </button>
        </div>

        {activeRentalTab === "readings" && (

        <section className="rental-panel monthly-readings-panel">
            <div className="panel-toolbar">
              <div>
                <h2>Monthly Meter Readings</h2>
                <span>
                  Enter or update the current month reading for every rental machine.
                </span>
              </div>

              <div className="monthly-panel-month">
                <CalendarDays size={16} />
                <span>Month</span>
                <strong>{monthLabel(billingMonth)}</strong>
              </div>
            </div>

            <div className="rental-filter-bar table-filter-bar">
              <div className="rental-search-box">
                <Search size={17} />
                <input
                  type="text"
                  value={searchText}
                  onChange={handleSearchChange}
                  placeholder="Search customer, machine, serial number or code..."
                  autoComplete="off"
                  aria-label="Search rental customer or machine"
                />
                {searchText && (
                  <button
                    type="button"
                    className="rental-search-clear"
                    onClick={handleReset}
                    aria-label="Clear search"
                    title="Clear search"
                  >
                    <X size={15} />
                  </button>
                )}
              </div>

              <label className="rental-select-filter">
                <span>Payment</span>
                <select
                  value={paymentFilter}
                  onChange={(event) => setPaymentFilter(event.target.value)}
                  aria-label="Filter by payment status"
                >
                  <option value="ALL">All Payments</option>
                  <option value="PENDING">Pending</option>
                  <option value="RECEIVED">Received</option>
                </select>
              </label>

              <label className="rental-select-filter">
                <span>Reading</span>
                <select
                  value={readingFilter}
                  onChange={(event) => setReadingFilter(event.target.value)}
                  aria-label="Filter by reading status"
                >
                  <option value="ALL">All Readings</option>
                  <option value="UPDATED">Updated</option>
                  <option value="NOT_UPDATED">Not Updated</option>
                </select>
              </label>

              <label className="month-filter">
                <CalendarDays size={16} />
                <span>Month</span>
                <input
                  type="month"
                  value={billingMonth}
                  onChange={(event) => setBillingMonth(event.target.value)}
                />
              </label>

              <button
                type="button"
                className="rental-reset-btn"
                onClick={handleReset}
                disabled={
                  !searchText &&
                  billingMonth === activeBillingMonth &&
                  paymentFilter === "ALL" &&
                  readingFilter === "ALL"
                }
              >
                <RotateCcw size={15} />
                Reset
              </button>
            </div>

            {loading ? (
              <div className="rental-loading">
                <RefreshCw size={23} className="spin" />
                <span>Loading rental readings...</span>
              </div>
            ) : searchText.trim() ? (
              <div className="rental-search-results">
                {filteredCustomerGroups.length === 0 ? (
                  <div className="rental-search-empty">
                    <div className="rental-empty-icon">
                      <Search size={22} />
                    </div>
                    <strong>No matching customer or machine</strong>
                    <span>
                      Try a customer name, machine name, serial number,
                      customer code or phone number.
                    </span>
                  </div>
                ) : (
                  <>
                    <div className="search-results-heading">
                      <div>
                        <strong>
                          {filteredCustomerGroups.length} matching customer
                          {filteredCustomerGroups.length === 1 ? "" : "s"}
                        </strong>
                        <span>
                          Select a customer and machine to view complete monthly history.
                        </span>
                      </div>
                      <span className="search-results-count">
                        {filteredCustomerMachineCount} machine{filteredCustomerMachineCount === 1 ? "" : "s"}
                      </span>
                    </div>

                    <div className="customer-search-results">
                      {filteredCustomerGroups.map((group) => (
                        <div
                          key={group.customerId}
                          className={`customer-result-card ${
                            Number(selectedCustomerId) === Number(group.customerId)
                              ? "selected"
                              : ""
                          }`}
                        >
                          <button
                            type="button"
                            className="customer-result-main"
                            onClick={() => openCustomer(group)}
                          >
                            <span className="customer-avatar">
                              {getInitials(group.customerName)}
                            </span>

                            <span className="customer-result-info">
                              <strong>{group.customerName}</strong>
                              <small>
                                {group.customerCode || "Customer"}
                                {group.customerPhone
                                  ? ` • ${group.customerPhone}`
                                  : ""}
                              </small>
                            </span>

                            <span className="customer-result-machine-count">
                              {group.machines.length} machine
                              {group.machines.length === 1 ? "" : "s"}
                            </span>

                            {Number(selectedCustomerId) === Number(group.customerId) ? (
                              <ChevronUp size={17} />
                            ) : (
                              <ChevronDown size={17} />
                            )}
                          </button>

                          {Number(selectedCustomerId) === Number(group.customerId) && (
                            <div className="customer-result-details">
                              <div className="machine-select-row">
                                <label>
                                  <span>Select Machine</span>
                                  <select
                                    value={selectedMachineId ?? ""}
                                    onChange={(event) =>
                                      selectMachine(event.target.value)
                                    }
                                  >
                                    {group.machines.map((row) => (
                                      <option
                                        key={row.machine.id}
                                        value={row.machine.id}
                                      >
                                        {row.machineName} • {row.serialNumber}
                                      </option>
                                    ))}
                                  </select>
                                </label>

                                <div className="selected-machine-mini">
                                  <span>Current machine</span>
                                  <strong>
                                    {selectedMachine?.machineName || "—"}
                                  </strong>
                                  <small>
                                    {selectedMachine?.machineNumber || "—"}
                                  </small>
                                </div>
                              </div>

                              {selectedMachine && (
                                <div className="selected-machine-history">
                                  <div className="history-heading">
                                    <div>
                                      <span className="history-kicker">
                                        Complete Monthly History
                                      </span>
                                      <h3>
                                        {selectedMachine.machineName}
                                      </h3>
                                      <p>
                                        {selectedMachine.machineNumber}
                                        {" • "}
                                        {selectedMachine.serialNumber}
                                      </p>
                                    </div>

                                    <div className="history-current-rate">
                                      <span>Price / Copy</span>
                                      <strong>
                                        {formatMoney(
                                          selectedMachine.billPrice ||
                                            selectedMachine.price
                                        )}
                                      </strong>
                                    </div>
                                  </div>

                                  <div className="history-machine-summary">
                                    <div>
                                      <span>Current Reading</span>
                                      <strong>
                                        {formatNumber(
                                          selectedMachine.monthlyReading ??
                                            selectedMachine.currentReading
                                        )}
                                      </strong>
                                    </div>
                                    <div>
                                      <span>History Records</span>
                                      <strong>
                                        {selectedMachineHistory.length}
                                      </strong>
                                    </div>
                                    <div>
                                      <span>Total Copies</span>
                                      <strong>
                                        {formatNumber(
                                          selectedHistoryTotals.copies
                                        )}
                                      </strong>
                                    </div>
                                    <div>
                                      <span>Total Amount</span>
                                      <strong>
                                        {formatMoney(
                                          selectedHistoryTotals.amount
                                        )}
                                      </strong>
                                    </div>
                                  </div>

                                  {selectedMachineHistory.length === 0 ? (
                                    <div className="history-empty">
                                      <Printer size={24} />
                                      <strong>No monthly history yet</strong>
                                      <span>
                                        A saved reading for this machine will
                                        appear here.
                                      </span>
                                    </div>
                                  ) : (
                                    <div className="history-table-wrap">
                                      <table className="machine-history-table">
                                        <thead>
                                          <tr>
                                            <th>Billing Month</th>
                                            <th>Previous Reading</th>
                                            <th>New Reading</th>
                                            <th>Price / Copy</th>
                                            <th>Copies</th>
                                            <th>Amount</th>
                                            <th>Status</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {selectedMachineHistory.map((row) => (
                                            <tr key={row.id || row.month}>
                                              <td>
                                                <strong className="history-month">
                                                  {monthLabel(row.month)}
                                                </strong>
                                              </td>
                                              <td>
                                                {formatNumber(row.previous)}
                                              </td>
                                              <td>
                                                <strong>
                                                  {formatNumber(row.current)}
                                                </strong>
                                              </td>
                                              <td>
                                                {formatMoney(row.price)}
                                              </td>
                                              <td>
                                                <strong>
                                                  {formatNumber(row.copies)}
                                                </strong>
                                              </td>
                                              <td>
                                                <strong className="history-amount">
                                                  {formatMoney(row.amount)}
                                                </strong>
                                              </td>
                                              <td>
                                                <span
                                                  className={`history-status-pill ${
                                                    String(row.status)
                                                      .toUpperCase() ===
                                                    "RECEIVED"
                                                      ? "received"
                                                      : "pending"
                                                  }`}
                                                >
                                                  {String(row.status)
                                                    .toUpperCase() ===
                                                  "RECEIVED"
                                                    ? "Received"
                                                    : "Pending"}
                                                </span>
                                              </td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
            ) : rentalRows.length === 0 ? (
              <div className="empty-state">
                <Printer size={42} />
                <strong>
                  {filteredRentalRows.length === 0 &&
                  (paymentFilter !== "ALL" || readingFilter !== "ALL")
                    ? "No customers match these filters"
                    : "No rental machines found"}
                </strong>
                <span>
                  {filteredRentalRows.length === 0 &&
                  (paymentFilter !== "ALL" || readingFilter !== "ALL")
                    ? "Try another payment or reading filter."
                    : "Add rental machines to customers in Customer / Machine Master."}
                </span>
              </div>
            ) : (
              <>
                <div className="rental-filter-summary">
                  <span>
                    Showing <strong>{filteredRentalRows.length}</strong> of{" "}
                    <strong>{rentalRows.length}</strong> rental machines
                  </span>
                  {(paymentFilter !== "ALL" || readingFilter !== "ALL") && (
                    <span className="active-filter-summary">
                      {paymentFilter !== "ALL"
                        ? paymentFilter === "RECEIVED"
                          ? "Received payments"
                          : "Pending payments"
                        : ""}
                      {paymentFilter !== "ALL" && readingFilter !== "ALL" ? " • " : ""}
                      {readingFilter !== "ALL"
                        ? readingFilter === "UPDATED"
                          ? "Reading updated"
                          : "Reading not updated"
                        : ""}
                    </span>
                  )}
                </div>

                <div className="rental-table-wrap">
                  <table className="rental-readings-table">
                    <colgroup>
                      <col className="col-number" />
                      <col className="col-customer" />
                      <col className="col-machine" />
                      <col className="col-serial" />
                      <col className="col-reading" />
                      <col className="col-reading" />
                      <col className="col-billing-month" />
                      <col className="col-price" />
                      <col className="col-copies" />
                      <col className="col-amount" />
                      <col className="col-status" />
                      <col className="col-actions" />
                    </colgroup>
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Customer</th>
                        <th>Machine</th>
                        <th>Serial Number</th>
                        <th>Old Reading</th>
                        <th>New Reading <em>*</em></th>
                        <th>Billing Month</th>
                        <th>Price / Copy (₹)</th>
                        <th>Copies</th>
                        <th>Amount (₹)</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>

                    <tbody>
                      {filteredRentalRows.map((row, index) => {
                        const machineId = row.machine.id;
                        const draftReading = draftReadings[machineId] ?? "";
                        const draftPrice = draftPrices[machineId] ?? String(row.price || 0);
                        const numericReading = draftReading === "" ? NaN : Number(draftReading);
                        const numericPrice = draftPrice === "" ? NaN : Number(draftPrice);
                        const invalidReading =
                          draftReading !== "" &&
                          (!Number.isInteger(numericReading) || numericReading < row.previousReading);
                        const copies =
                          Number.isInteger(numericReading) && !invalidReading
                            ? Math.max(0, numericReading - row.previousReading)
                            : row.bill
                              ? row.copies
                              : 0;
                        const amount =
                          Number.isFinite(numericPrice) && Number.isInteger(numericReading) && !invalidReading
                            ? copies * numericPrice
                            : row.bill
                              ? row.amount
                              : 0;
                        const isSaving = savingMachineId === machineId;
                        const submitted = Boolean(row.bill);
                        const draftStatus =
                          String(draftPaymentStatuses[machineId] ?? (submitted ? row.status : "PENDING"))
                            .toUpperCase();
                        const existingStatus =
                          String(row.status || "PENDING").toUpperCase();
                        const hasChanges =
                          draftReading !== "" &&
                          (Number(draftReading) !== Number(row.monthlyReading ?? row.currentReading) ||
                            Number(draftPrice) !== Number(row.billPrice ?? row.price) ||
                            draftStatus !== existingStatus);

                        return (
                          <tr key={machineId}>
                            <td className="row-number">{index + 1}</td>

                            <td>
                              <div className="table-customer-cell">
                                <strong>{row.customerName}</strong>
                                <div>
                                  {row.customerCode && <span>{row.customerCode}</span>}
                                  {row.customerPhone && <small>{row.customerPhone}</small>}
                                </div>
                              </div>
                            </td>

                            <td>
                              <div className="table-machine-cell">
                                <strong>{row.machineName}</strong>
                                <small>{row.machineNumber}</small>
                              </div>
                            </td>

                            <td>
                              <span className="serial-cell">{row.serialNumber}</span>
                            </td>

                            <td>
                              <span className="old-reading-cell">{formatNumber(row.previousReading)}</span>
                            </td>

                            <td>
                              <input
                                className={`reading-table-input ${invalidReading ? "invalid" : ""}`}
                                type="number"
                                min={row.previousReading}
                                step="1"
                                value={draftReading}
                                onChange={(event) => updateDraftReading(machineId, event.target.value)}
                                placeholder="Enter reading"
                                aria-label={`New reading for ${row.customerName} ${row.machineName}`}
                              />
                            </td>

                            <td>
                              <span className="billing-month-cell">
                                {monthLabel(getBillMonth(row.bill) || billingMonth)}
                              </span>
                            </td>

                            <td>
                              <div className="price-table-input">
                                <span>₹</span>
                                <input
                                  type="number"
                                  min="0"
                                  step="0.01"
                                  value={draftPrice}
                                  onChange={(event) => updateDraftPrice(machineId, event.target.value)}
                                  aria-label={`Price per copy for ${row.machineName}`}
                                />
                              </div>
                            </td>

                            <td>
                              <strong className="copies-cell">{formatNumber(copies)}</strong>
                            </td>

                            <td>
                              <strong className={`amount-cell ${amount > 0 ? "has-value" : ""}`}>
                                {formatMoney(amount).replace("₹ ", "")}
                              </strong>
                            </td>

                            <td>
                              <select
                                className={`payment-status-select ${
                                  draftStatus === "RECEIVED" ? "received" : "pending"
                                }`}
                                value={draftStatus === "RECEIVED" ? "RECEIVED" : "PENDING"}
                                onChange={(event) =>
                                  setDraftPaymentStatuses((previous) => ({
                                    ...previous,
                                    [machineId]: event.target.value,
                                  }))
                                }
                                aria-label={`Payment status for ${row.customerName} ${row.machineName}`}
                              >
                                <option value="PENDING">Pending</option>
                                <option value="RECEIVED">Received</option>
                              </select>
                            </td>

                            <td>
                              <div className="table-action-group">
                                <button
                                  type="button"
                                  className="table-save-btn"
                                  onClick={() => handleSaveMachine(row)}
                                  disabled={
                                    isSaving ||
                                    !Number.isFinite(numericPrice) ||
                                    numericPrice < 0 ||
                                    draftReading === "" ||
                                    invalidReading ||
                                    (submitted && !hasChanges)
                                  }
                                  title={submitted ? "Update monthly reading" : "Save monthly reading"}
                                >
                                  {isSaving ? (
                                    <RefreshCw size={14} className="spin" />
                                  ) : (
                                    <Save size={14} />
                                  )}
                                  {isSaving ? "Saving" : submitted ? "Update" : "Save"}
                                </button>

                                <button
                                  type="button"
                                  className="table-reset-btn"
                                  onClick={() => {
                                    setDraftReadings((previous) => ({
                                      ...previous,
                                      [machineId]: submitted
                                        ? String(row.monthlyReading ?? row.currentReading)
                                        : "",
                                    }));
                                    setDraftPrices((previous) => ({
                                      ...previous,
                                      [machineId]: String(row.price),
                                    }));
                                    setDraftPaymentStatuses((previous) => ({
                                      ...previous,
                                      [machineId]: submitted
                                        ? String(row.status || "PENDING").toUpperCase()
                                        : "PENDING",
                                    }));
                                  }}
                                  title="Reset row"
                                  disabled={isSaving}
                                >
                                  <RotateCcw size={14} />
                                </button>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>

                    <tfoot>
                      <tr>
                        <td colSpan="8" className="table-total-label">
                          Monthly Total
                        </td>
                        <td>
                          <strong>{formatNumber(rentalRows.reduce((sum, row) => {
                            const value = Number(draftReadings[row.machine.id]);
                            return sum + (Number.isInteger(value) && value >= row.previousReading ? value - row.previousReading : row.copies);
                          }, 0))}</strong>
                        </td>
                        <td>
                          <strong>{formatMoney(rentalRows.reduce((sum, row) => {
                            const value = Number(draftReadings[row.machine.id]);
                            const price = Number(draftPrices[row.machine.id] ?? row.price);
                            const copies = Number.isInteger(value) && value >= row.previousReading ? value - row.previousReading : row.copies;
                            return sum + (copies * (Number.isFinite(price) ? price : 0));
                          }, 0))}</strong>
                        </td>
                        <td colSpan="2"></td>
                      </tr>
                    </tfoot>
                  </table>
                </div>

                <div className="rental-table-note">
                  <span>
                    <strong>Old Reading</strong> is the confirmed previous meter. <strong>New Reading</strong> is the value entered by the customer or admin.
                  </span>
                  <span>
                    Amount = (New Reading − Old Reading) × Price / Copy
                  </span>
                </div>
              </>
            )}
          </section>

        )}

        {activeRentalTab === "invoices" && (
        <section className="rental-panel rental-invoices-panel">
          <div className="panel-toolbar rental-invoice-toolbar">
            <div className="rental-invoice-heading">
              <h2>Rental Bills & Invoices</h2>
              <span>
                Monthly rental bills generated for customers and machines.
              </span>
            </div>

            <div className="rental-invoice-toolbar-actions">
              <form
                className="rental-invoice-search-form"
                onSubmit={(event) => event.preventDefault()}
                role="search"
              >
                <label className="rental-invoice-search-input-wrap">
                  <Search size={16} aria-hidden="true" />
                  <input
                    type="search"
                    value={invoiceSearchInput}
                    onChange={(event) => setInvoiceSearchInput(event.target.value)}
                    placeholder="Search customer, month, serial no., machine, amount..."
                    aria-label="Search rental invoices by bill number, customer, month, serial number, machine, readings or amount"
                  />
                  {invoiceSearchInput && (
                    <button
                      type="button"
                      className="rental-invoice-search-clear"
                      onClick={() => setInvoiceSearchInput("")}
                      aria-label="Clear invoice search"
                      title="Clear search"
                    >
                      <X size={14} />
                    </button>
                  )}
                </label>
                {invoiceSearchLoading && (
                  <span
                    className="rental-invoice-search-spinner"
                    role="status"
                    aria-live="polite"
                    aria-label="Searching invoices"
                    title="Searching invoices..."
                  >
                    <RefreshCw size={15} className="spin" />
                  </span>
                )}
              </form>

              <button
                type="button"
                className="create-rental-bill-inline-btn"
                onClick={openCreateRentalBill}
              >
                <Plus size={15} />
                Create New Rental Bill
              </button>
            </div>
          </div>

          {invoiceRows.length === 0 ? (
            <div className="rental-invoice-empty">
              <FileText size={30} />
              <strong>No rental bills generated yet</strong>
              <span>
                Create a new rental bill to see the customer, machine,
                monthly reading and invoice here.
              </span>
            </div>
          ) : filteredInvoiceRows.length === 0 ? (
            <div className="rental-invoice-empty">
              <Search size={30} />
              <strong>No matching invoices found</strong>
              <span>Try a customer name, billing month, serial number, machine, bill number, reading or amount.</span>
              <button type="button" className="invoice-view-btn" onClick={() => setInvoiceSearchInput("")}>Clear search</button>
            </div>
          ) : (
            <div className="rental-invoice-table-wrap" onScroll={handleInvoiceTableScroll}>
              <table className="rental-invoice-table">
                <thead>
                  <tr>
                    <th>Bill No.</th>
                    <th>Customer</th>
                    <th>Machine</th>
                    <th>Serial Number</th>
                    <th>Billing Month</th>
                    <th>Previous Reading</th>
                    <th>New Reading</th>
                    <th>Chargeable Copies</th>
                    <th>Amount</th>
                    <th>Invoice PDF</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {visibleInvoiceRows.map((invoice) => (
                    <tr key={invoice.id}>
                      <td>
                        <strong className="invoice-number-cell">
                          {invoice.invoiceNumber}
                        </strong>
                      </td>
                      <td>
                        <div className="invoice-customer-cell">
                          <strong>{invoice.customerName}</strong>
                        </div>
                      </td>
                      <td>
                        <div className="invoice-machine-cell">
                          <strong>{invoice.machineName}</strong>
                        </div>
                      </td>
                      <td>
                        <span className="invoice-serial-cell">
                          {invoice.serialNumber || "—"}
                        </span>
                      </td>
                      <td>
                        <span className="invoice-month-cell">
                          {monthLabel(invoice.billingMonth)}
                        </span>
                      </td>
                      <td>{formatNumber(invoice.previousReading)}</td>
                      <td>
                        <strong>
                          {formatNumber(invoice.currentReading)}
                        </strong>
                      </td>
                      <td>
                        {formatNumber(invoice.chargeableCopies)}
                      </td>
                      <td>
                        <strong className="invoice-amount-cell">
                          {formatMoney(invoice.grandTotal)}
                        </strong>
                      </td>
                      <td>
                        <div className="invoice-action-buttons">
                          <button
                            type="button"
                            className="invoice-view-btn"
                            onClick={() => setInvoicePreview(invoice)}
                            title="View invoice"
                          >
                            <Eye size={14} />
                            View
                          </button>

                          <button
                            type="button"
                            className="invoice-pdf-btn"
                            onClick={() => printRentalInvoice(invoice)}
                            title="Print / Save invoice as PDF"
                          >
                            <Download size={14} />
                            PDF
                          </button>
                        </div>
                      </td>
                      <td>
                        <div className="invoice-action-buttons">
                          <button
                            type="button"
                            className="invoice-view-btn"
                            onClick={() => openEditRentalBill(invoice)}
                            title="Edit readings"
                          >
                            <Pencil size={14} />
                            Update
                          </button>
                          <button
                            type="button"
                            className="invoice-delete-btn"
                            style={{ background: "#b42318", color: "#fff", border: "1px solid #b42318" }}
                            onClick={() => handleDeleteRentalBill(invoice)}
                            disabled={deletingBillId === Number(invoice.serverBillId ?? invoice.id)}
                            title="Cancel rental bill"
                          >
                            <Trash2 size={14} />
                            {deletingBillId === Number(invoice.serverBillId ?? invoice.id) ? "..." : "Delete"}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {visibleInvoiceCount < filteredInvoiceRows.length && (
                <div className="rental-invoice-lazy-status" role="status">
                  <RefreshCw size={13} className="spin" />
                  <span>Scroll down to load more invoices ({visibleInvoiceCount} of {filteredInvoiceRows.length})</span>
                </div>
              )}
            </div>
          )}
        </section>
        )}

        {/* =====================================================
            CREATE RENTAL BILL DRAWER
        ===================================================== */}
        {billDrawerOpen && (
          <div
            className="rental-bill-drawer-overlay"
            role="presentation"
            onMouseDown={(event) => {
              if (event.target === event.currentTarget) {
                closeCreateRentalBill();
              }
            }}
          >
            <aside
              className="rental-bill-drawer"
              role="dialog"
              aria-modal="true"
              aria-labelledby="create-rental-bill-title"
            >
              <div className="rental-bill-drawer-header">
                <div>
                  <h2 id="create-rental-bill-title">
                    {editingInvoice ? "Update Rental Bill" : "Create New Rental Bill"}
                  </h2>
                  <p>
                    {editingInvoice ? "Change the meter readings and save the updated bill." : "Select a customer and machine, then enter readings for each print type to calculate the bill."}
                  </p>
                </div>

                <button
                  type="button"
                  className="rental-bill-close-btn"
                  onClick={closeCreateRentalBill}
                  disabled={generatingInvoice}
                  aria-label="Close"
                >
                  <X size={19} />
                </button>
              </div>

              <div className="rental-bill-form">
                <section className="rental-bill-section">
                  <div className="rental-bill-section-title">
                    <Users size={16} />
                    Select Customer & Machine
                  </div>

                  <div className="rental-bill-grid">
                    <div className="rental-bill-field full rental-customer-search-field">
                      <span>Customer <em>*</em></span>
                      <div className="rental-customer-search-wrap">
                        <Search size={15} className="rental-customer-search-icon" />
                        <input
                          type="text"
                          value={billCustomerSearch}
                          onChange={handleBillCustomerSearchChange}
                          disabled={Boolean(editingInvoice)}
                          onFocus={() => !editingInvoice && setBillCustomerSearchOpen(true)}
                          onBlur={() => {
                            window.setTimeout(() => setBillCustomerSearchOpen(false), 150);
                          }}
                          placeholder="Search customer by name, code, phone or email..."
                          autoComplete="off"
                        />
                        {billCustomerSearchOpen && (
                          <div className="rental-customer-search-results">
                            {filteredBillCustomers.length > 0 ? (
                              filteredBillCustomers.map((customer) => (
                                <button
                                  type="button"
                                  className="rental-customer-search-option"
                                  key={customer.id}
                                  onMouseDown={(event) => event.preventDefault()}
                                  onClick={() => selectBillCustomer(customer)}
                                >
                                  <span className="customer-search-option-main">
                                    {getCustomerName(customer)}
                                  </span>
                                  <span className="customer-search-option-meta">
                                    {getCustomerCode(customer) || "No code"}
                                    {getCustomerPhone(customer)
                                      ? ` • ${getCustomerPhone(customer)}`
                                      : ""}
                                  </span>
                                </button>
                              ))
                            ) : (
                              <div className="rental-customer-search-empty rental-customer-search-empty-create">
                                <div className="rental-customer-search-empty-icon">
                                  <Users size={18} />
                                </div>

                                <strong>No customer found</strong>

                                <span>
                                  Create a new customer using the details you entered.
                                </span>

                                <button
                                  type="button"
                                  className="rental-create-customer-inline-btn"
                                  onMouseDown={(event) => event.preventDefault()}
                                  onClick={() =>
                                    handleAddCustomer(billCustomerSearch)
                                  }
                                >
                                  <Plus size={15} />
                                  Create New Customer
                                </button>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>

                    <label className="rental-bill-field full">
                      <span>Machine <em>*</em></span>
                      <select
                        value={billMachineId}
                        onChange={handleBillMachineChange}
                        disabled={!billCustomerId || Boolean(editingInvoice)}
                      >
                        <option value="">
                          {billCustomerId
                            ? "Select machine"
                            : "Select customer first"}
                        </option>
                        {billCustomerMachines.map((machine) => (
                          <option
                            key={machine.id}
                            value={machine.id}
                          >
                            {getMachineName(machine)} •{" "}
                            {getMachineSerial(machine)}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>
                </section>

                {billMachineRow?.machine && (
                  <>
                    <section className="rental-bill-section">
                      <div className="rental-bill-section-title">
                        <CalendarDays size={16} />
                        Meter Readings — A4 / A3
                        <small>Enter the new reading for each print type. Rates are loaded from the assigned machine.</small>
                      </div>

                      <div className="rental-print-reading-grid">
                        {[
                          { key: "a4_bw", label: "A4 Black & White", rate: getMachineA4BWRate(billMachineRow.machine), previousKeys: ["a4_bw_previous_meter", "a4_bw_current_meter", "a4_bw_opening_meter"] },
                          { key: "a4_color", label: "A4 Color", rate: getMachineA4ColorRate(billMachineRow.machine), previousKeys: ["a4_color_previous_meter", "a4_color_current_meter", "a4_color_opening_meter"] },
                          { key: "a3_bw", label: "A3 Black & White", rate: getMachineA3BWRate(billMachineRow.machine), previousKeys: ["a3_bw_previous_meter", "a3_bw_current_meter", "a3_bw_opening_meter"] },
                          { key: "a3_color", label: "A3 Color", rate: getMachineA3ColorRate(billMachineRow.machine), previousKeys: ["a3_color_previous_meter", "a3_color_current_meter", "a3_color_opening_meter"] },
                        ].map((item) => {
                          const machine = billMachineRow.machine;
                          const specificPrevious = item.previousKeys
                            .map((key) => machine?.[key])
                            .find((value) => value !== undefined && value !== null && value !== "");
                          const previous = Number(
                            editingInvoice?.printPreviousReadings?.[item.key] ??
                            specificPrevious ??
                            billCalculation.printBreakdown.find((row) => row.key === item.key)?.previous ??
                            0
                          );
                          const currentValue = billPrintReadings[item.key] ?? "";
                          return (
                            <div className="rental-print-reading-card" key={item.key}>
                              <div className="rental-print-reading-card-heading">
                                <strong>{item.label}</strong>
                                <span>Rate: {formatMoney(item.rate)} / copy</span>
                              </div>
                              <div className="rental-print-reading-allowance" style={{ fontSize: 12, color: "#526782", margin: "6px 0" }}>
                                Monthly free allowance: <strong>{formatNumber(getMachineFreeCopiesForType(billMachineRow.machine, item.key))}</strong> copies
                              </div>
                              <div className="rental-print-reading-fields">
                                <div className="rental-bill-readonly-field">
                                  <span>Previous Reading</span>
                                  <strong>{formatNumber(previous)}</strong>
                                </div>
                                <label className="rental-bill-field">
                                  <span>New Reading <em>*</em></span>
                                  <input
                                    type="number"
                                    min={previous}
                                    step="1"
                                    value={currentValue}
                                    onChange={(event) => setBillPrintReadings((old) => ({ ...old, [item.key]: event.target.value }))}
                                    placeholder="Enter reading"
                                  />
                                </label>
                              </div>
                              {(() => {
                                const copiesUsed = Math.max(
                                  0,
                                  Number(currentValue === "" ? previous : currentValue) - previous
                                );
                                const freeAllowanceForType = getMachineFreeCopiesForType(billMachineRow.machine, item.key);
                                const chargeableForType = Math.max(copiesUsed - freeAllowanceForType, 0);
                                const printPrice = chargeableForType * Number(item.rate || 0);
                                return (
                                  <div
                                    className="rental-print-reading-copies"
                                    style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10, flexWrap: "wrap" }}
                                  >
                                    <span>
                                      Copies used: <strong>{formatNumber(copiesUsed)}</strong>
                                      {" · "}Free: <strong>{formatNumber(Math.min(copiesUsed, freeAllowanceForType))}</strong>
                                      {" · "}Chargeable: <strong>{formatNumber(chargeableForType)}</strong>
                                    </span>
                                    <span className="rental-print-reading-price" style={{ whiteSpace: "nowrap" }}>
                                      Price: <strong>{formatMoney(printPrice)}</strong>
                                    </span>
                                  </div>
                                );
                              })()}
                            </div>
                          );
                        })}
                      </div>

                      <div className="rental-bill-grid rental-print-reading-footer">
                        <label className="rental-bill-field">
                          <span>GST (%)</span>
                          <input
                            type="number"
                            min="0"
                            max="100"
                            step="0.01"
                            value={billGSTPercent}
                            onChange={(event) => setBillGSTPercent(event.target.value)}
                            aria-label="GST percentage"
                            required
                          />
                        </label>
                      </div>

                      <div className="rental-bill-date-summary" style={{ marginTop: 14 }}>
                        <div className="rental-bill-date-card" style={{ padding: "14px 16px", border: "1px solid #bfd4ff", borderRadius: 12, background: "#f3f7ff" }}>
                          <label style={{ display: "block", color: "#526782", fontSize: 12, fontWeight: 800, marginBottom: 8 }}>
                            BILLING MONTH *
                            <input
                              type="month"
                              value={billBillingMonth || getCurrentMonth()}
                              onChange={(event) => {
                                setBillBillingMonth(event.target.value || getCurrentMonth());
                                setInvoicePreview(null);
                              }}
                              required
                              style={{ display: "block", marginTop: 8, width: "min(100%, 360px)", padding: "10px 12px", border: "1px solid #b8cbed", borderRadius: 8, background: "white", color: "#163b78", fontWeight: 700 }}
                            />
                          </label>
                          <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
                            <strong style={{ color: "#163b78", fontSize: 20, fontWeight: 800 }}>{monthLabel(billBillingMonth || getCurrentMonth())}</strong>
                            <span style={{ color: "#526782", fontSize: 13, fontWeight: 700 }}>Bill date: {new Date().toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })} · Due in 15 days</span>
                          </div>
                        </div>
                      </div>
                    </section>

                    <section className="rental-bill-section">
                      <div className="rental-bill-section-title">
                        <IndianRupee size={16} />
                        Bill Calculation
                      </div>

                      <div className="rental-bill-calculation">
                        <div>
                          <span>Total Copies</span>
                          <strong>
                            {formatNumber(
                              billCalculation.usedCopies
                            )}
                          </strong>
                        </div>

                        <div>
                          <span>Free Copies Deducted</span>
                          <strong>
                            {formatNumber(billCalculation.freeCopies)}
                          </strong>
                        </div>

                        <div>
                          <span>Chargeable Copies</span>
                          <strong>
                            {formatNumber(
                              billCalculation.chargeableCopies
                            )}
                          </strong>
                        </div>

                        <div>
                          <span>Copy Charges</span>
                          <strong>
                            {formatMoney(
                              billCalculation.copyCharges
                            )}
                          </strong>
                        </div>

                        <div>
                          <span>Fixed Rental</span>
                          <strong>
                            {formatMoney(
                              billCalculation.fixedRent
                            )}
                          </strong>
                        </div>

                        <div>
                          <span>Subtotal</span>
                          <strong>
                            {formatMoney(
                              billCalculation.subtotal
                            )}
                          </strong>
                        </div>

                        <div>
                          <span>
                            GST ({billCalculation.gstPercent}%)
                          </span>
                          <strong>
                            {formatMoney(
                              billCalculation.gstAmount
                            )}
                          </strong>
                        </div>

                        <div className="rental-bill-grand-total">
                          <span>Grand Total</span>
                          <strong>
                            {formatMoney(
                              billCalculation.grandTotal
                            )}
                          </strong>
                        </div>
                      </div>
                    </section>
                  </>
                )}

                {invoicePreview && (
                  <section className="rental-bill-preview">
                    <div>
                      <span>Generated Invoice</span>
                      <strong>
                        {invoicePreview.invoiceNumber}
                      </strong>
                    </div>
                    <button
                      type="button"
                      onClick={() =>
                        printRentalInvoice(invoicePreview)
                      }
                    >
                      <Download size={14} />
                      Download PDF
                    </button>
                  </section>
                )}
              </div>

              <div className="rental-bill-drawer-footer">
                <button
                  type="button"
                  className="rental-bill-cancel-btn"
                  onClick={closeCreateRentalBill}
                  disabled={generatingInvoice}
                >
                  {invoicePreview ? "Close" : "Cancel"}
                </button>

                {invoicePreview ? (
                  <button
                    type="button"
                    className="rental-bill-generate-btn"
                    onClick={() => printRentalInvoice(invoicePreview)}
                  >
                    <Download size={15} />
                    Download PDF
                  </button>
                ) : (
                  <button
                    type="button"
                    className="rental-bill-generate-btn"
                    onClick={handleGenerateInvoice}
                    disabled={
                      generatingInvoice ||
                      !billCustomerId ||
                      !billMachineId ||
                      [billPrintReadings.a4_bw, billPrintReadings.a4_color, billPrintReadings.a3_bw, billPrintReadings.a3_color].some((value) => value === "")
                    }
                  >
                    {generatingInvoice ? (
                      <><RefreshCw size={15} className="spin" /> Saving...</>
                    ) : (
                      <><Save size={15} /> {editingInvoice ? "Update Bill" : "Save Bill"}</>
                    )}
                  </button>
                )}
              </div>
            </aside>
          </div>
        )}

        {invoicePreview && !billDrawerOpen && (
          <div
            className="rental-invoice-preview-overlay"
            role="presentation"
            onMouseDown={(event) => {
              if (event.target === event.currentTarget) {
                setInvoicePreview(null);
              }
            }}
          >
            <div
              className="rental-invoice-preview-modal"
              role="dialog"
              aria-modal="true"
            >
              <div className="rental-invoice-preview-header">
                <div>
                  <span>Rental Invoice</span>
                  <h2>{invoicePreview.invoiceNumber}</h2>
                </div>
                <button
                  type="button"
                  onClick={() => setInvoicePreview(null)}
                >
                  <X size={18} />
                </button>
              </div>

              <div className="rental-invoice-preview-body">
                <div className="invoice-preview-customer">
                  <div>
                    <span>Customer</span>
                    <strong>{invoicePreview.customerName}</strong>
                  </div>
                  <div>
                    <span>Machine</span>
                    <strong>{invoicePreview.machineName}</strong>
                  </div>
                  <div>
                    <span>Serial Number</span>
                    <strong>{invoicePreview.serialNumber}</strong>
                  </div>
                  <div>
                    <span>Billing Month</span>
                    <strong>
                      {monthLabel(invoicePreview.billingMonth)}
                    </strong>
                  </div>
                </div>

                <div className="invoice-preview-readings">
                  <div>
                    <span>Previous Reading</span>
                    <strong>
                      {formatNumber(invoicePreview.previousReading)}
                    </strong>
                  </div>
                  <div>
                    <span>New Reading</span>
                    <strong>
                      {formatNumber(invoicePreview.currentReading)}
                    </strong>
                  </div>
                  <div>
                    <span>Copies Used</span>
                    <strong>
                      {formatNumber(invoicePreview.usedCopies)}
                    </strong>
                  </div>
                  <div>
                    <span>Free Copies</span>
                    <strong>
                      {formatNumber(invoicePreview.freeCopies)}
                    </strong>
                  </div>
                  <div>
                    <span>Chargeable Copies</span>
                    <strong>
                      {formatNumber(invoicePreview.chargeableCopies)}
                    </strong>
                  </div>
                </div>

                <div className="invoice-preview-total-box">
                  <div>
                    <span>Fixed Rental</span>
                    <strong>
                      {formatMoney(invoicePreview.fixedRent)}
                    </strong>
                  </div>
                  <div>
                    <span>Copy Charges</span>
                    <strong>
                      {formatMoney(invoicePreview.copyCharges)}
                    </strong>
                  </div>
                  <div>
                    <span>Subtotal</span>
                    <strong>
                      {formatMoney(invoicePreview.subtotal)}
                    </strong>
                  </div>
                  <div>
                    <span>
                      GST ({invoicePreview.gstPercent}%)
                    </span>
                    <strong>
                      {formatMoney(invoicePreview.gstAmount)}
                    </strong>
                  </div>
                  <div className="preview-grand-total">
                    <span>Grand Total</span>
                    <strong>
                      {formatMoney(invoicePreview.grandTotal)}
                    </strong>
                  </div>
                </div>
              </div>

              <div className="rental-invoice-preview-footer">
                <button
                  type="button"
                  className="rental-bill-cancel-btn"
                  onClick={() => setInvoicePreview(null)}
                >
                  Close
                </button>
                <button
                  type="button"
                  className="rental-bill-generate-btn"
                  onClick={() => printRentalInvoice(invoicePreview)}
                >
                  <Download size={15} />
                  Save / Print PDF
                </button>
              </div>
            </div>
          </div>
        )}

        {rolloverModalOpen && (
          <div
            className="rental-modal-backdrop"
            role="presentation"
            onMouseDown={(event) => {
              if (event.target === event.currentTarget) {
                setRolloverModalOpen(false);
              }
            }}
          >
            <div
              className="rental-confirm-modal"
              role="dialog"
              aria-modal="true"
              aria-labelledby="start-new-month-title"
            >
              <div className="rental-confirm-icon">
                <RotateCcw size={22} />
              </div>

              <h3 id="start-new-month-title">Start New Month?</h3>

              <p>
                This will start{" "}
                <strong>
                  {monthLabel(
                    rolloverTargetMonth || getNextMonth(billingMonth)
                  )}
                </strong>{" "}
                for all rental machines.
              </p>

              <div className="rollover-info-box">
                <div>
                  <strong>Previous reading</strong>
                  <span>
                    The latest confirmed machine reading becomes the starting reading for the new cycle.
                  </span>
                </div>
                <div>
                  <strong>New reading</strong>
                  <span>
                    New customer readings start empty for the new month.
                  </span>
                </div>
                <div>
                  <strong>History preserved</strong>
                  <span>
                    Existing monthly bills are not deleted or changed.
                  </span>
                </div>
              </div>

              <div className="rental-confirm-warning">
                <AlertTriangle size={16} />
                <span>
                  Monthly bill persistence is handled by the rental-billing API. This action changes the admin screen to the next reading cycle.
                </span>
              </div>

              <div className="rental-confirm-actions">
                <button
                  type="button"
                  className="rental-cancel-btn"
                  onClick={() => setRolloverModalOpen(false)}
                  disabled={rollingOver}
                >
                  Cancel
                </button>

                <button
                  type="button"
                  className="rental-confirm-btn"
                  onClick={confirmStartNewMonth}
                  disabled={rollingOver}
                >
                  {rollingOver ? (
                    <>
                      <RefreshCw size={15} className="spin" />
                      Starting...
                    </>
                  ) : (
                    <>
                      <RotateCcw size={15} />
                      Start New Month
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* =================================================
            SHARED CUSTOMER FORM
            This is the exact same form used on Customers.
            It includes per-machine rental terms and the
            A4/A3 B/W + Color billing rates.
        ================================================= */}
        {customerFormWasOpen && customerFormSelection?.__create && (
          <div className="rental-shared-customer-form-layer">
            <CustomerForm />
          </div>
        )}
      </main>
    </div>
  );
}
