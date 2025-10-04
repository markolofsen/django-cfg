/**
 * Payment Form Component
 * Handles payment creation form functionality with real provider currencies
 */
function paymentForm() {
    return {
        loading: false,
        loadingCurrencies: false,
        form: {
            user: '',
            amount_usd: '',
            currency_code: '',
            provider: 'nowpayments',
            description: '',
            callback_url: '',
            cancel_url: ''
        },
        currencies: [],
        allCurrencies: [],
        providers: [
            { value: 'nowpayments', name: 'NowPayments', display_name: 'NowPayments' }
        ],
        conversionResult: null,
        users: [],
        errorMessage: '',

        async init() {
            console.log('🚀 PaymentForm: Initializing...');
            console.log('🔍 PaymentAPI object:', window.PaymentAPI);
            console.log('🔍 PaymentAPI.currencies:', window.PaymentAPI?.currencies);
            console.log('🔍 PaymentAPI.admin:', window.PaymentAPI?.admin);
            await this.loadInitialData();
        },

        async loadInitialData() {
            console.log('📊 PaymentForm: Loading initial data...');
            this.loading = true;
            try {
                // Load all currencies and provider-specific currencies
                await Promise.all([
                    this.loadAllCurrencies(),
                    this.loadProviderCurrencies(),
                    this.loadUsers()
                ]);
                console.log('✅ PaymentForm: Initial data loaded successfully');
            } catch (error) {
                console.error('❌ PaymentForm: Failed to load initial data:', error);
                PaymentAPI.utils.showNotification('Failed to load form data', 'error');
            } finally {
                this.loading = false;
            }
        },

        async loadAllCurrencies() {
            console.log('💰 PaymentForm: Loading all currencies...');
            console.log('🔍 PaymentAPI.currencies.supported type:', typeof PaymentAPI.currencies.supported);
            try {
                if (typeof PaymentAPI.currencies.supported !== 'function') {
                    console.error('❌ PaymentAPI.currencies.supported is not a function:', PaymentAPI.currencies.supported);
                    console.log('🔍 Available currencies methods:', Object.keys(PaymentAPI.currencies));
                    return;
                }
                const data = await PaymentAPI.currencies.supported();
                console.log('📊 Currencies API response:', data);
                this.allCurrencies = data.currencies?.currencies || data.currencies || [];
                console.log('✅ Loaded currencies:', this.allCurrencies.length);
            } catch (error) {
                console.error('❌ Failed to load currencies:', error);
            }
        },

        async loadProviderCurrencies() {
            if (!this.form.provider) {
                console.log('⚠️ PaymentForm: No provider selected, skipping currency load');
                return;
            }
            
            console.log('🏦 PaymentForm: Loading provider currencies for:', this.form.provider);
            console.log('🔍 PaymentAPI.currencies.byProvider type:', typeof PaymentAPI.currencies.byProvider);
            
            this.loadingCurrencies = true;
            try {
                if (typeof PaymentAPI.currencies.byProvider !== 'function') {
                    console.error('❌ PaymentAPI.currencies.byProvider is not a function:', PaymentAPI.currencies.byProvider);
                    console.log('🔍 Available currencies methods:', Object.keys(PaymentAPI.currencies));
                    return;
                }
                
                // Use the provider-currencies API endpoint directly
                const response = await PaymentAPI.request(`/api/payments/provider-currencies/by_provider/?provider=${this.form.provider}`);
                console.log('📊 Provider currencies API response:', response);
                
                // Extract currencies for the specific provider
                const providerData = response.currencies_by_provider?.[this.form.provider];
                this.currencies = providerData?.currencies || [];
                
                console.log('🔍 Sample currency structure:', this.currencies[0]);
                
                console.log('✅ Loaded provider currencies:', this.currencies.length);
                
                // If current currency is not supported by provider, reset it
                if (this.form.currency_code && !this.currencies.find(c => c.provider_currency_code === this.form.currency_code)) {
                    console.log('⚠️ Current currency not supported by provider, resetting');
                    this.form.currency_code = '';
                    this.conversionResult = null;
                }
            } catch (error) {
                console.error('❌ Failed to load provider currencies:', error);
                this.currencies = [];
            } finally {
                this.loadingCurrencies = false;
            }
        },

        async loadUsers() {
            console.log('👥 PaymentForm: Loading users...');
            console.log('🔍 PaymentAPI.admin:', PaymentAPI.admin);
            console.log('🔍 PaymentAPI.admin?.users:', PaymentAPI.admin?.users);
            console.log('🔍 PaymentAPI.admin?.users?.list type:', typeof PaymentAPI.admin?.users?.list);
            
            try {
                if (!PaymentAPI.admin) {
                    console.error('❌ PaymentAPI.admin is undefined');
                    this.users = [{ id: '', username: 'Select User', email: '' }];
                    return;
                }
                
                if (!PaymentAPI.admin.users) {
                    console.error('❌ PaymentAPI.admin.users is undefined');
                    this.users = [{ id: '', username: 'Select User', email: '' }];
                    return;
                }
                
                if (typeof PaymentAPI.admin.users.list !== 'function') {
                    console.error('❌ PaymentAPI.admin.users.list is not a function:', PaymentAPI.admin.users.list);
                    this.users = [{ id: '', username: 'Select User', email: '' }];
                    return;
                }
                
                const data = await PaymentAPI.admin.users.list();
                console.log('📊 Users API response:', data);
                this.users = data.results || data || [];
                
                // If no users loaded, try to get current user info
                if (this.users.length === 0) {
                    console.warn('⚠️ No users loaded from admin API');
                    this.users = [{ id: '', username: 'Select User', email: '' }];
                } else {
                    console.log('✅ Loaded users:', this.users.length);
                }
            } catch (error) {
                console.error('❌ Failed to load users:', error);
                // Set empty option for user selection
                this.users = [{ id: '', username: 'Select User', email: '' }];
            }
        },

        async onProviderChange() {
            await this.loadProviderCurrencies();
        },

        async onAmountOrCurrencyChange() {
            if (this.form.amount_usd && this.form.currency_code && this.form.currency_code !== 'USD') {
                await this.convertCurrency();
            } else {
                this.conversionResult = null;
            }
        },

        async convertCurrency() {
            if (!this.form.amount_usd || !this.form.currency_code) return;
            
            try {
                // Get the original currency code for conversion (not provider code)
                const currencyInfo = this.getCurrencyInfo(this.form.currency_code);
                const originalCurrencyCode = currencyInfo.currency?.code || this.form.currency_code;
                
                const result = await PaymentAPI.currencies.convert('USD', originalCurrencyCode, this.form.amount_usd);
                this.conversionResult = {
                    amount: result.converted_amount,
                    rate: result.rate,
                    currency: originalCurrencyCode
                };
            } catch (error) {
                console.error('Currency conversion failed:', error);
                this.conversionResult = null;
            }
        },

        getCurrencyInfo(providerCurrencyCode) {
            return this.currencies.find(c => c.provider_currency_code === providerCurrencyCode) || 
                   this.allCurrencies.find(c => c.code === providerCurrencyCode) || 
                   { provider_currency_code: providerCurrencyCode, currency: { code: providerCurrencyCode, name: providerCurrencyCode, currency_type: 'unknown' } };
        },

        validateForm() {
            const errors = [];
            
            if (!this.form.user) errors.push('User is required');
            if (!this.form.amount_usd || this.form.amount_usd <= 0) errors.push('Valid amount is required');
            if (!this.form.currency_code) errors.push('Currency is required');
            if (!this.form.provider) errors.push('Provider is required');
            
            return errors;
        },

        clearError() {
            this.errorMessage = '';
        },

        async submitForm() {
            // Clear previous error
            this.clearError();
            
            const errors = this.validateForm();
            if (errors.length > 0) {
                this.errorMessage = errors.join(', ');
                PaymentAPI.utils.showNotification('Please fix form errors', 'error');
                return;
            }

            this.loading = true;
            
            try {
                const data = await PaymentAPI.admin.payments.create(this.form);
                PaymentAPI.utils.showNotification('Payment created successfully!', 'success');
                window.location.href = `/cfg/admin/django_cfg_payments/admin/payments/${data.id}/`;
            } catch (error) {
                console.error('Error:', error);
                
                // Show detailed error in form
                this.errorMessage = error.message || 'Failed to create payment';
                
                // Show brief notification
                PaymentAPI.utils.showNotification('Payment creation failed', 'error');
            } finally {
                this.loading = false;
            }
        }
    };
}
