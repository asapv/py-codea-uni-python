from typing import List, Dict
import tkinter as tk
from tkinter import ttk, messagebox


class CutOffCalculator:
    """Clase para calcular la Ley de Corte usando el método de Kenneth Lane (simplificado)."""

    def __init__(self, mining_cost: float, processing_cost: float, mineral_price: float, refining_cost: float,
                 metallurgical_recovery: float, stock_threshold: float) -> None:
        """
        Inicializa la calculadora de Ley de Corte.

        :param mining_cost: Costo de minado por tonelada ($/t).
        :type mining_cost: float
        :param processing_cost: Costo de procesamiento por tonelada ($/t).
        :type processing_cost: float
        :param mineral_price: Precio del mineral por tonelada y por porcentaje ($/t).
        :type mineral_price: float
        :param refining_cost: Costo de refinación por tonelada y por porcentaje ($/t).
        :type refining_cost: float
        :param metallurgical_recovery: Recuperación metalúrgica como porcentaje (%).
        :type metallurgical_recovery: float
        :param stock_threshold: Umbral para enviar a stock (porcentaje de la ley de corte).
        :type stock_threshold: float
        """
        self.mining_cost: float = mining_cost
        self.processing_cost: float = processing_cost
        self.mineral_price: float = mineral_price
        self.refining_cost: float = refining_cost
        self.metallurgical_recovery: float = metallurgical_recovery / 100  # Convertir porcentaje a decimal
        self.stock_threshold: float = stock_threshold
        self.cutoff_grade: float = self.calculate_cutoff_grade()

    def calculate_cutoff_grade(self) -> float:
        """
        Calcula la Ley de Corte usando la fórmula:
        Ley de Corte = (Cm + Cp) / ((Pm - Cr) * RM)

        :return: Ley de Corte calculada.
        :rtype: float
        """
        denominator: float = (self.mineral_price - self.refining_cost) * self.metallurgical_recovery
        if denominator <= 0:
            raise ValueError("El precio del mineral ajustado por refinación y recuperación debe ser mayor que 0.")

        return ((self.mining_cost + self.processing_cost) / denominator) * 100

    def decide_block_action(self, block_grade: float) -> str:
        """
        Decide si un bloque debe ser procesado, enviado a stock o descartado.

        :param block_grade: Ley del bloque a evaluar.
        :type block_grade: float
        :return: Acción recomendada para el bloque.
        :rtype: str
        """
        stock_limit: float = self.cutoff_grade * self.stock_threshold
        if block_grade >= self.cutoff_grade:
            return "Procesar"
        elif block_grade >= stock_limit:
            return "Enviar a stock"
        else:
            return "Descartar"

    def process_multiple_blocks(self, block_grades: List[float]) -> List[Dict[str, float]]:
        """
        Procesa múltiples bloques y devuelve las decisiones para cada uno.

        :param block_grades: Lista de leyes de los bloques.
        :type block_grades: List[float]
        :return: Lista de diccionarios con las leyes y decisiones.
        :rtype: List[Dict[str, float]]
        """
        results: List[Dict[str, float]] = []
        for grade in block_grades:
            action: str = self.decide_block_action(grade)
            results.append({"grade": grade, "action": action})
        return results


class CutOffApp:
    """Clase para la interfaz gráfica de la Calculadora de Ley de Corte."""

    def __init__(self, root: tk.Tk) -> None:
        """
        Inicializa la interfaz gráfica.

        :param root: Ventana principal de tkinter.
        :type root: tk.Tk
        """
        self.root: tk.Tk = root
        self.root.title("Calculadora de Ley de Corte")
        self.block_grades: List[float] = []

        # Crear y organizar los widgets
        self.setup_ui()

    def setup_ui(self) -> None:
        """Configura los elementos de la interfaz gráfica."""
        # Frame para los datos de entrada
        input_frame = ttk.LabelFrame(self.root, text="Datos de Entrada", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Campos de entrada
        ttk.Label(input_frame, text="Costo de Minado ($/tonelada):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.mining_cost_entry = ttk.Entry(input_frame)
        self.mining_cost_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Costo de Procesamiento ($/tonelada):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.processing_cost_entry = ttk.Entry(input_frame)
        self.processing_cost_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Precio del Mineral ($/tonelada):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.mineral_price_entry = ttk.Entry(input_frame)
        self.mineral_price_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Costo de Refinación ($/tonelada):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.refining_cost_entry = ttk.Entry(input_frame)
        self.refining_cost_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Recuperación Metalúrgica (%):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.recovery_entry = ttk.Entry(input_frame)
        self.recovery_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Umbral para Stock (0-1):").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.stock_threshold_entry = ttk.Entry(input_frame)
        self.stock_threshold_entry.grid(row=5, column=1, padx=5, pady=5)

        # Entrada para leyes de bloques
        ttk.Label(input_frame, text="Ley del Bloque (%):").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.block_grade_entry = ttk.Entry(input_frame)
        self.block_grade_entry.grid(row=6, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Agregar Bloque", command=self.add_block).grid(row=6, column=2, padx=5, pady=5)

        # Frame para los botones de acción
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Calcular", command=self.calculate).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.clear).grid(row=0, column=1, padx=5)

        # Frame para los resultados
        result_frame = ttk.LabelFrame(self.root, text="Resultados", padding=10)
        result_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Tabla para mostrar resultados
        self.result_tree = ttk.Treeview(result_frame, columns=("Grade", "Action"), show="headings", height=5)
        self.result_tree.heading("Grade", text="Ley del Bloque (%)")
        self.result_tree.heading("Action", text="Acción")
        self.result_tree.column("Grade", width=100, anchor="center")
        self.result_tree.column("Action", width=150, anchor="center")
        self.result_tree.grid(row=0, column=0, padx=5, pady=5)

        # Etiqueta para la Ley de Corte
        self.cutoff_label = ttk.Label(result_frame, text="Ley de Corte: N/A")
        self.cutoff_label.grid(row=1, column=0, padx=5, pady=5)

        # Etiqueta para el resumen
        self.summary_label = ttk.Label(result_frame, text="Resumen: N/A")
        self.summary_label.grid(row=2, column=0, padx=5, pady=5)

    def validate_positive_number(self, value: str, field_name: str, max_value: float = None) -> float:
        """
        Valida que un valor ingresado sea un número positivo y, opcionalmente, esté dentro de un rango.

        :param value: Valor ingresado como string.
        :type value: str
        :param field_name: Nombre del campo para el mensaje de error.
        :type field_name: str
        :param max_value: Valor máximo permitido (opcional).
        :type max_value: float
        :return: Valor convertido a float.
        :rtype: float
        :raises ValueError: Si el valor no es un número positivo o no está dentro del rango.
        """
        try:
            num: float = float(value)
            if num <= 0:
                raise ValueError(f"{field_name} debe ser mayor que 0.")
            if field_name == "Umbral para Stock" and (num < 0 or num > 1):
                raise ValueError("El umbral para stock debe estar entre 0 y 1.")
            if field_name == "Recuperación Metalúrgica" and (num < 0 or num > 100):
                raise ValueError("La recuperación metalúrgica debe estar entre 0 y 100%.")
            if max_value is not None and num > max_value:
                raise ValueError(f"{field_name} no puede ser mayor que {max_value}.")
            return num
        except ValueError as e:
            if "must be" in str(e) or "debe estar entre" in str(e) or "no puede ser mayor" in str(e):
                raise
            raise ValueError(f"{field_name} debe ser un número válido.")

    def add_block(self) -> None:
        """Agrega la ley de un bloque a la lista."""
        try:
            grade: float = self.validate_positive_number(self.block_grade_entry.get(), "Ley del Bloque")
            self.block_grades.append(grade)
            self.block_grade_entry.delete(0, tk.END)
            messagebox.showinfo("Éxito", f"Bloque con ley {grade}% agregado.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def calculate(self) -> None:
        """Realiza el cálculo de la Ley de Corte y muestra los resultados."""
        try:
            mining_cost: float = self.validate_positive_number(self.mining_cost_entry.get(), "Costo de Minado")
            processing_cost: float = self.validate_positive_number(self.processing_cost_entry.get(),
                                                                   "Costo de Procesamiento")
            mineral_price: float = self.validate_positive_number(self.mineral_price_entry.get(), "Precio del Mineral")
            refining_cost: float = self.validate_positive_number(self.refining_cost_entry.get(), "Costo de Refinación",
                                                                 max_value=mineral_price)
            recovery: float = self.validate_positive_number(self.recovery_entry.get(), "Recuperación Metalúrgica")
            stock_threshold: float = self.validate_positive_number(self.stock_threshold_entry.get(),
                                                                   "Umbral para Stock")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        if not self.block_grades:
            messagebox.showerror("Error", "Debe agregar al menos un bloque.")
            return

        try:
            calculator: CutOffCalculator = CutOffCalculator(mining_cost, processing_cost, mineral_price, refining_cost,
                                                            recovery, stock_threshold)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        # Mostrar Ley de Corte
        self.cutoff_label.config(text=f"Ley de Corte: {calculator.cutoff_grade:.2f}%")

        # Procesar bloques
        results: List[Dict[str, float]] = calculator.process_multiple_blocks(self.block_grades)

        # Limpiar tabla
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        # Mostrar resultados en la tabla
        for result in results:
            self.result_tree.insert("", tk.END, values=(f"{result['grade']:.2f}", result["action"]))

        # Mostrar resumen
        processed: int = sum(1 for r in results if r["action"] == "Procesar")
        stocked: int = sum(1 for r in results if r["action"] == "Enviar a stock")
        discarded: int = sum(1 for r in results if r["action"] == "Descartar")
        summary_text: str = f"Resumen:\nProcesados: {processed}\nEnviados a Stock: {stocked}\nDescartados: {discarded}"
        self.summary_label.config(text=summary_text)

    def clear(self) -> None:
        """Limpia todos los campos y resultados."""
        self.mining_cost_entry.delete(0, tk.END)
        self.processing_cost_entry.delete(0, tk.END)
        self.mineral_price_entry.delete(0, tk.END)
        self.refining_cost_entry.delete(0, tk.END)
        self.recovery_entry.delete(0, tk.END)
        self.stock_threshold_entry.delete(0, tk.END)
        self.block_grade_entry.delete(0, tk.END)
        self.block_grades.clear()
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        self.cutoff_label.config(text="Ley de Corte: N/A")
        self.summary_label.config(text="Resumen: N/A")


if __name__ == "__main__":
    root = tk.Tk()
    app = CutOffApp(root)
    root.mainloop()