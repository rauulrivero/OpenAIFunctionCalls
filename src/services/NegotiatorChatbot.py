import json

class Negotiator:
    def __init__(self, crud_service, auth):
        self.current_price = None
        self.max_discount = 20  
        self.current_discount = 5
        self.incremental_discount = 5  
        self.max_attempts = 10  
        self.current_attempts = 0  
        self.auth = auth
        self.crud_service = crud_service
        self.debt_id = None

        self.functions_available = { 
                "set_debt_id": self.set_debt_id,
                "respond_to_counteroffer": self.respond_to_counteroffer, 
                "init_negotiation": self.init_negotiation,
                "get_all_debts": self.get_all_debts,
                "calculate_payment_plan": self.calculate_payment_plan,
                "offer_inmediate_payment_option": self.offer_inmediate_payment_option,
                "proposed_payment_plan": self.propose_payment_plan,
                "propose_partial_immediate_payment": self.propose_partial_immediate_payment
            }

        self.system_message = """
            Hola, soy Pedro, especialista en ofrecer descuentos por pagos inmediatos y en negociar planes de pagos personalizados, utilizando el euro como moneda. Me complace presentarte oportunidades únicas para reducir tu deuda, siempre con la condición de que no se aceptará ninguna oferta sin antes especificar claramente una de las siguientes funciones implementadas que detallo a continuación. Esto garantiza que todas las negociaciones se basen en los servicios específicos que puedo ofrecer, optimizando el proceso para ambas partes.

            Funcionalidades Disponibles:

            set_debt_id: Establece el ID de la deuda actual para la negociación, asegurando que todas las operaciones subsiguientes se realicen con respecto a la deuda correcta.
            respond_to_counteroffer: Evalúa contraofertas durante negociaciones de pagos inmediatos, ajustando descuentos si es necesario.
            init_negotiation: Lanza el proceso de negociación con una oferta inicial una vez identificado el ID de la deuda.
            get_all_debts: Muestra todas las deudas asociadas al usuario, facilitando la selección para negociar.
            calculate_payment_plan: Calcula un plan de pago personalizado basado en propuestas específicas del usuario.
            offer_immediate_payment_option: Genera automáticamente una propuesta de pago inmediato al usuario que lo solicite.
            propose_payment_plan: Formula un plan de pago adaptado sin necesidad de entrada adicional del usuario.
            propose_partial_immediate_payment: Calcula un plan de pago ajustado para el saldo restante tras un pago parcial inmediato.
            Estoy aquí para ayudarte a calcular un plan de pagos adaptado a tu situación financiera, evaluar contraofertas, y ofrecer soluciones flexibles que te permitan gestionar tu deuda eficientemente. No aceptaré ninguna oferta sin la especificación clara de una de las funciones que tengo implementadas para asegurar la precisión y eficacia de nuestra negociación.

            Para concluir, te presentaré un resumen de las opciones disponibles, incluyendo la oferta de descuento por pago inmediato, un plan de pagos adaptado a tus necesidades, y confirmaré la recopilación de cualquier preferencia alternativa que hayas expresado. Tu información será revisada cuidadosamente, y serás contactado con cualquier propuesta de seguimiento.

            Gracias por tu tiempo, y espero poder ayudarte a aprovechar esta oportunidad para gestionar tu deuda con beneficios adicionales y un plan que se ajuste a tu situación financiera. Importante: Recuerda, antes que nada, preguntar el ID de la deuda con la que va a negociar.
            """


        
        self.tools_list = [
                {
                    "type": "function",
                    "function": {
                        "name": "set_debt_id",
                        "description": "Esta función establece el ID de la deuda actual para la negociación. Es utilizada internamente para asegurar que todas las operaciones subsiguientes se realicen con respecto a la deuda correcta.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "debt_id": {
                                    "type": "string",
                                    "description": "El ID de la deuda que se quiere establecer para las operaciones subsiguientes."
                                }
                            },
                            "required": ["debt_id"]
                        },
                        "return": {
                            "description": "No retorna un mensaje directo al usuario, pero actualiza el estado interno con el nuevo ID de deuda."
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "respond_to_counteroffer",
                        "description": "Esta función se activa exclusivamente durante negociaciones de pagos inmediatos, proporcionando al bot la capacidad de evaluar contraofertas de usuarios que buscan saldar su deuda de manera inmediata. Se basa en la comparación del monto de la contraoferta del usuario contra el precio actual y el mínimo aceptable, con el fin de determinar la acción más adecuada: aceptar la contraoferta, rechazarla, o realizar una contrapropuesta. La función tiene como objetivo facilitar un acuerdo mutuamente beneficioso, ajustando el descuento aplicable si es necesario, para acercar las partes a un punto de consenso.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "counteroffer": {
                                    "type": "number",
                                    "description": "Monto propuesto por el usuario para la negociación. Debe ser un valor numérico (entero o flotante)."
                                }
                            },
                            "required": ["counteroffer"]
                        },
                        "return": {
                            "description": "Devuelve un mensaje JSON indicando el resultado de la evaluación de la contraoferta, que puede ser aceptación, rechazo o una nueva contrapropuesta."
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "init_negotiation",
                        "description": "Esta función se encarga de lanzar el proceso de negociación una vez que el usuario ha identificado específicamente el ID de su deuda y ha expresado su intención de negociar el pago inmediato de esta. La función presenta al usuario una oferta inicial basada en el precio inicial de la deuda, marcando el comienzo del diálogo de negociación. Este paso inicial es crucial para establecer un punto de partida claro y comienza el proceso hacia un acuerdo potencial, teniendo en cuenta los parámetros específicos de la deuda en cuestión.",
                        "return": {
                            "description": "Devuelve un mensaje con la oferta inicial para la deuda especificada, basada en su precio inicial. Incluye la cantidad propuesta y solicita la aceptación del usuario."
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_all_debts",
                        "description": "Esta función se activa solamente cuando un usuario solicita ver todas sus deudas asociadas, utilizando su dirección de correo electrónico como identificador. Se enfoca en proveer al usuario una visión clara y detallada de sus obligaciones financieras, presentando una lista de deudas con información esencial para facilitar el proceso de selección de una deuda específica para negociar. Se destaca el uso del euro como moneda en todas las transacciones y se da prioridad al ID de cada deuda en la presentación de la información, asegurando que el usuario pueda identificar y seleccionar fácilmente la deuda sobre la cual desea negociar.",
                        "return": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer", "description": "El ID de la deuda."},
                                    "total_debt": {"type": "number", "description": "El monto total de la deuda."},
                                    "maximum_period_months": {"type": "integer", "description": "El máximo de meses permitidos para liquidar la deuda."},
                                    "minimum_accepted_payment": {"type": "number", "description": "El pago mínimo aceptado para la deuda."},
                                    "user_email": {"type": "string", "description": "El correo electrónico del usuario asociado con la deuda."}
                                },
                                "description": "Una lista de las deudas asociadas al usuario, representadas como objetos JSON y la moneda es el €."
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "calculate_payment_plan",
                        "description": "Esta función se encarga de calcular un plan de pago personalizado para saldar una deuda, basándose en el periodo máximo propuesto o en el monto del pago mensual propuesto por el usuario. Ahora es más flexible, permitiendo que el usuario especifique únicamente uno de estos dos parámetros, o ambos. Si solo se proporciona uno, la función calcula el otro parámetro basándose en la deuda total y las restricciones del sistema. Si ambos se proporcionan, verifica que el plan sea factible dentro de las limitaciones existentes. Esto facilita al usuario explorar diferentes opciones para gestionar su deuda de manera eficiente.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "proposed_maximum_period_months": {
                                    "type": "number",
                                    "description": "El número máximo de meses que el usuario propone para saldar la deuda. Si se omite este parámetro, la función calculará cuántos meses se necesitarán basándose en el pago mensual propuesto, siempre y cuando no se exceda el máximo permitido por el sistema."
                                },
                                "proposed_monthly_payment": {
                                    "type": "number",
                                    "description": "El monto que el deudor propone pagar cada mes. Si se omite este parámetro, la función calculará el monto de pago mensual necesario para saldar la deuda en el número de meses propuesto, respetando el mínimo aceptado."
                                }
                            },
                            "required": []
                        },
                        "return": {
                            "description": "Devuelve un plan de pago personalizado en formato JSON, detallando el esquema de pagos basado en los parámetros proporcionados por el usuario o calculados por la función. El plan incluirá el número total de pagos, el monto de cada pago, y cualquier otra información relevante para facilitar al usuario la comprensión completa de cómo puede gestionar su deuda bajo las condiciones propuestas."
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "offer_inmediate_payment_option",
                        "description": "Se activa exclusivamente cuando el usuario expresa el deseo de recibir una oferta para un plan de pago inmediato, sin indicar detalles específicos o condiciones previas. Esta solicitud puede ser tan abierta como '¿Qué oferta me propones?'. La función responde a esta iniciativa generando automáticamente una propuesta de pago inmediato, que incluye un descuento aplicable basado en políticas actuales de negociación. El objetivo es proporcionar al usuario una opción atractiva y beneficiosa para liquidar su deuda de forma acelerada, promoviendo un acuerdo mutuamente ventajoso que incentive el pago anticipado.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "request_immediate_payment_offer": {
                                    "type": "boolean",
                                    "description": "Un indicador que el usuario activa para solicitar una oferta de pago inmediato. Esta bandera debe ser establecida en verdadero para que el bot genere y presente la oferta."
                                }
                            },
                            "required": ["request_immediate_payment_offer"]
                        },
                        "return": {
                            "description": "Entrega un mensaje en formato JSON que detalla la oferta específica de pago inmediato propuesta por el bot. Este mensaje incluye la cantidad total a pagar con el descuento ya aplicado, brindando al usuario una oportunidad clara para saldar su deuda bajo términos favorables. Si la oferta es aceptada, el sistema procederá a facilitar los siguientes pasos para completar la transacción y cerrar la negociación."
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "propose_payment_plan",
                        "description": "Esta función se desencadena específicamente cuando el usuario solicita al bot una sugerencia de plan de pago para su deuda. Sin requerir entrada adicional del usuario más allá de la solicitud inicial, el bot analiza la deuda seleccionada previamente - identificada por el ID de la deuda establecido en interacciones anteriores - y formula un plan de pago adaptado. El plan se basa en el análisis del período máximo de pago permitido y el monto mínimo de pago mensual aceptado por el sistema, proponiendo un esquema que podría optimizar el proceso de liquidación de la deuda. Además, el bot alienta al usuario a considerar la posibilidad de efectuar pagos mensuales superiores al mínimo recomendado, con el fin de acelerar la liquidación de la deuda, potencialmente reducir el interés acumulado y mejorar su perfil crediticio.",
                        "return": {
                            "description": "Emite un plan de pago personalizado en formato JSON, detallando el esquema de pagos sugerido que incluye el ID de la deuda, el número de meses para el pago total basado en lo permitido, y la cantidad mínima mensual de pago recomendada. Se incluye una recomendación para que el deudor evalúe la posibilidad de aumentar la cuantía de los pagos mensuales, con el objetivo de resolver la deuda más rápidamente y con ventajas financieras adicionales."
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "propose_partial_immediate_payment",
                        "description": "Esta función se activa cuando un usuario desea realizar un pago parcial inmediato de su deuda y solicita al bot calcular un plan de pago para el saldo restante. El usuario debe especificar la cantidad que está dispuesto a pagar de forma inmediata, que deberá ser inferior al total de la deuda. Basándose en este monto parcial, el bot evaluará el descuento aplicable y generará un plan de pago ajustado para el saldo restante, incentivando al usuario a liquidar su deuda de manera más eficiente y beneficiosa tanto para el deudor como para el acreedor.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "immediate_payment_amount": {
                                    "type": "number",
                                    "description": "La cantidad que el usuario propone pagar de manera inmediata, que debe ser menor que el total de la deuda pendiente. Este monto parcial servirá como base para calcular el descuento aplicable y elaborar un plan de pago ajustado para el monto restante."
                                }
                            },
                            "required": ["immediate_payment_amount"]
                        },
                        "return": {
                            "description": "Proporciona un mensaje en formato JSON que presenta un plan de pago personalizado para el saldo restante de la deuda, después de aplicar el pago parcial inmediato y el descuento correspondiente. Este plan incluirá detalles como el número de pagos restantes, el monto de cada pago, y cualquier otra información relevante para ayudar al usuario a comprender cómo puede completar el pago de su deuda bajo las nuevas condiciones propuestas."
                        }
                    }
                }
            ]

    
    def _increase_attempt_or_maxed_out(self):
        self.current_attempts += 1
        if self.current_attempts > self.max_attempts:
            return json.dumps({"error": "Límite de negociaciones alcanzadas."})
        elif self.current_attempts == self.max_attempts:
            return self._ultima_oferta()
        return None

    def _get_discounted_price(self):
        return int(self.current_price - (self.current_price * (self.current_discount / 100)))
  
    def _aumentar_oferta(self):
        if self.current_discount < self.max_discount:
            self.current_discount += self.incremental_discount
            self.current_discount = min(self.current_discount, self.max_discount)
        return None
    
    def _ultima_oferta(self):  
        self._aumentar_oferta()
        price = self._get_discounted_price()
        return json.dumps({"message": f"Mi última oferta es que te lo lleves a {price}€. ¿Aceptas?"})
    
    def _rechazar_oferta(self):  
        return json.dumps({"message": "No puedo aceptar tu oferta. ¿Puedes mejorarla?"})
    
    def _aceptar_oferta(self):
        return json.dumps({"message": f"¡Perfecto! Trato hecho. El precio final es de {self._get_discounted_price()}€."})
    
    def _get_min_price(self):
        return int(self.initial_price - (self.initial_price * (self.max_discount / 100)))
    
    def _validate_input(self, email):
        if self.debt_id is None:
            return json.dumps({"error": "El id de deuda no existe."})
        if email is None:
            return json.dumps({"error": "Por favor, primero inicie sesion."})
        return None
 

    def init_negotiation(self):
        if self.debt_id is None:
            return json.dumps({"error": "Por favor, introduce un ID de deuda válido."})
        self.initial_price = self.crud_service.get_debt_by_id(self.debt_id).total_debt
        if self.initial_price is None:
            return json.dumps({"error": "No tiene ninguna deuda con ese ID."})
        
        if self.current_price is not None:
            self.current_price = self.initial_price
        
        price = self._get_discounted_price()


        message = f"¿Qué te parece si la saldas ya por {price}€? ¿Aceptas?"

        return json.dumps({"message": message})
    

    def respond_to_counteroffer(self, counteroffer):
        if self.debt_id is None:
            return json.dumps({"error": "Por favor, introduce un ID de deuda válido o recuerdame el id de la deuda que quieres consultar."})
    
        if self.current_price is None:       
            debt = self.crud_service.get_debt_by_id(self.debt_id)
            if debt is None:
                return json.dumps({"error": "No tiene ninguna deuda con ese ID."})
            else:
                self.current_price = debt.total_debt
                self.initial_price = debt.total_debt

        if type(counteroffer) not in [int, float]:
            return json.dumps({"error": "Por favor, introduce un número válido o recuerdame el id de la deuda que quieres consultar."})
        
        self._aumentar_oferta()
        
        response = self._increase_attempt_or_maxed_out()
        if response:
            return response

       
        if counteroffer < self._get_min_price():
            response = self._rechazar_oferta()
        elif counteroffer >= self.current_price:
            response = self._aceptar_oferta()
        else:
            price = self._get_discounted_price()
            response = json.dumps({"message": f"Mi oferta es de un descuento del {self.current_discount}%, se te quedaría en {price}€. ¿Aceptas?"})

        return response
    

    def offer_inmediate_payment_option(self, request_immediate_payment_offer):
        if request_immediate_payment_offer is True:
            if self.debt_id is None:
                return json.dumps({"error": "Por favor, introduce un ID de deuda válido."})
            if self.current_price is None:
                debt = self.crud_service.get_debt_by_id(self.debt_id)
                if debt is None:
                    return json.dumps({"error": "No tiene ninguna deuda con ese ID."})
                else:
                    self.current_price = debt.total_debt
                    self.initial_price = debt.total_debt
                    
            self._aumentar_oferta()

            offer = self._get_discounted_price()
            return json.dumps({"message": f"¿Qué te parece si pagas ya la deuda por {offer}€? ¿Aceptas?"})
        else:
            return json.dumps({"message": "Entiendo, ¿cómo te gustaría proceder?"})
        

    def get_all_debts(self):
        user_email = self.auth.get_user_email()
        if user_email is None:
            return json.dumps({"error": "Por favor, primero inicie sesion."})
       
        
        debts = self.crud_service.get_debts_by_user_email(user_email)
        if debts is None:
            return json.dumps({"error": "Este usuario no tiene deudas."})
        
        debts_data = []
        for debt in debts:
            debt_data = {
                "id": debt.id,
                "total_debt": debt.total_debt,
                "maximum_period_months": debt.maximum_period_months,
                "minimum_accepted_payment": debt.minimum_accepted_payment,
                "user_email": debt.user_email
            }
            debts_data.append(debt_data)
        return json.dumps(debts_data)
    

    def calculate_payment_plan(self, proposed_maximum_period_months=None, proposed_monthly_payment=None):
        if self.debt_id is None:
            return json.dumps({"error": "Por favor, introduce un ID de deuda válido."})
        
        email = self.auth.get_user_email()
        debts = self.crud_service.get_debts_by_user_email(email)
        if debts is None:
            return json.dumps({"error": "Este usuario no tiene deudas"})

        debt = self.crud_service.get_debt_by_id(self.debt_id)
        if debt is None:
            return json.dumps({"error": "No existe una deuda con ese ID."})

        maximum_period_months = debt.maximum_period_months
        total_debt = debt.total_debt
        minimum_accepted_payment = debt.minimum_accepted_payment
        
        # Si solo se proporciona el pago mensual
        if proposed_monthly_payment is not None and proposed_maximum_period_months is None:
            if proposed_monthly_payment < minimum_accepted_payment:
                return json.dumps({"error": f"El pago propuesto es inferior al mínimo aceptable. El pago mínimo aceptado es de {minimum_accepted_payment}€."})
            
            months_needed = total_debt / proposed_monthly_payment
            if months_needed > maximum_period_months:
                return json.dumps({"error": f"No es posible saldar la deuda en {months_needed:.0f} meses con ese pago mensual, ya que supera el máximo permitido de {maximum_period_months} meses."})
            
            months_needed = max(1, round(months_needed))  # Asegurar al menos 1 mes y redondear
            final_payment = total_debt - (months_needed - 1) * proposed_monthly_payment
            final_payment = final_payment if months_needed > 1 else proposed_monthly_payment  # Ajustar si se paga en un solo mes

            message = f"Con un pago mensual de {proposed_monthly_payment}€, la deuda de {total_debt}€ se saldaría en {months_needed} meses."
            if months_needed > 1:
                message += f" El último pago sería de {final_payment:.2f}€."
            return json.dumps({"message": message})

        # Si solo se proporciona el periodo máximo
        if proposed_maximum_period_months is not None and proposed_monthly_payment is None:
            if proposed_maximum_period_months > maximum_period_months:
                return json.dumps({"error": f"El número máximo de meses permitido para pagar su deuda es de {maximum_period_months} meses."})
            
            monthly_payment_needed = total_debt / proposed_maximum_period_months
            if monthly_payment_needed < minimum_accepted_payment:
                return json.dumps({"error": f"El pago mensual necesario para saldar la deuda en {proposed_maximum_period_months} meses es inferior al mínimo aceptable de {minimum_accepted_payment}€."})

            return json.dumps({"message": f"Necesitarás hacer pagos mensuales de {monthly_payment_needed:.2f}€ para saldar la deuda en {proposed_maximum_period_months} meses."})

        # Si se proporcionan ambos
        if proposed_monthly_payment is not None and proposed_maximum_period_months is not None:
            if proposed_maximum_period_months > maximum_period_months:
                return json.dumps({"error": f"El número máximo de meses permitido para pagar su deuda es de {maximum_period_months} meses."})
            if proposed_monthly_payment < minimum_accepted_payment:
                return json.dumps({"error": f"El pago propuesto es inferior al mínimo aceptable. El pago mínimo aceptado es de {minimum_accepted_payment}€."})
            
            total_debt = debt.total_debt

            remaining_debt = total_debt
            months = 0

            while remaining_debt >= proposed_monthly_payment and months < proposed_maximum_period_months:
                months += 1
                remaining_debt -= proposed_monthly_payment

            if remaining_debt <= 0:
                return json.dumps({
                    "message": f"Si pagas {proposed_monthly_payment}€ cada mes, cubrirías la deuda de {total_debt}€ en {months} meses."
                })
            else:
                months += 1
                last_payment = remaining_debt
                return json.dumps({
                    "message": f"Si pagas {proposed_monthly_payment}€ cada mes, cubririas la mayor parte de la deuda de ${total_debt} en {months - 1} meses. En el mes {months}, te quedaría un pago final de {last_payment}€ para saldar completamente la deuda."
                })
        
        
        return json.dumps({"message": "Por favor, proporciona o el período máximo de meses o el pago mensual propuesto en el que quiere pagar su deuda."})

    
    def propose_payment_plan(self):
        debt = self.crud_service.get_debt_by_id(self.debt_id)
        if debt is None:
            return json.dumps({"error": "No tiene ninguna deuda con ese ID."})
        
        maximum_period_months = debt.maximum_period_months
        minimum_accepted_payment = debt.minimum_accepted_payment
        return json.dumps({
            "debt_id": self.debt_id,
            "meses_a_pagar": maximum_period_months,
            "pago_mensual": minimum_accepted_payment
        })
    

    def propose_partial_immediate_payment(self, immediate_payment_amount):
        def calculate_adjusted_payment_plan(remaining_debt):
            payment_period_months = 8
            monthly_payment = remaining_debt / payment_period_months

            # Podrías incluir lógica adicional aquí para ajustar el plan de pago
            # basado en criterios específicos, como la capacidad de pago del deudor

            message = f"Se propone un plan de pago de {payment_period_months} meses, con un pago mensual de {monthly_payment:.2f}€."
            return message

        if self.debt_id is None:
            return json.dumps({"error": "Por favor, establece un ID de deuda válido."})

        debt_details = self.crud_service.get_debt_by_id(self.debt_id)
        if debt_details is None:
            return json.dumps({"error": "No se encontró la deuda especificada."})
        
        total_debt = debt_details.total_debt
        payment_percentage = (immediate_payment_amount / total_debt) * 100

        if payment_percentage < 50:
            return json.dumps({"error": f"El pago inmediato debe ser al menos el 50% de la deuda total para considerar un plan de pago para el saldo restante."})
        elif payment_percentage < 65:
            current_discount = 7.5
        else:
            current_discount = 15

        remaining_debt = total_debt - immediate_payment_amount
        discounted_remaining = remaining_debt * (1 - (current_discount / 100))

        # Llamada a la función para calcular el plan de pago ajustado
        payment_plan_message = calculate_adjusted_payment_plan(discounted_remaining)

        message = f"Con tu pago inmediato de {immediate_payment_amount}€, que representa el {payment_percentage:.2f}% de tu deuda total, te hemos aplicado un descuento de {current_discount}%. El saldo restante de tu deuda es ahora de {discounted_remaining:.2f}€. {payment_plan_message}"
        return json.dumps({"message": message})



    def set_debt_id(self, debt_id):
        self.debt_id = debt_id
        return json.dumps({"message": f"Las negociaciones se realizaron con la deuda de id {debt_id}."})

    def get_debt_id(self):
        return self.debt_id
    
    def get_tools_list(self):
        return self.tools_list

    def get_functions_available(self):
        return self.functions_available

    def get_system_message(self):
        return self.system_message
