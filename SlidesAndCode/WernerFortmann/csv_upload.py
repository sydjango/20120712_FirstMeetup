# Author: Werner Fortmann <werner.fortmann@gmail.com>
#
# Note: this code is modified from working code, and thus won't work '
# as is. It is designed to demonstrate possible implementation of 
# a multi state CSV upload.

class UploadCSV_View1(FormView):

  template_name = 'uploadcsv_view1.html'
  form_class = UploadFileForm

  def form_valid(self,form):
    form = self.form_class(self.request.POST, self.request.FILES)
    if form.is_valid():
		from pandas.io.parsers import read_csv

		fh = self.request.FILES['docfile']
		csv_df = read_csv(filepath_or_buffer = fh)
		self.request.session['assettrans_csvupload_df'] = csv_df

		return HttpResponseRedirect(reverse('UploadCSV_view2', 
			kwargs={'pk':self.kwargs['pk']}))
    else:
		return self.render_to_response(self.get_context_data(form=form))
      
class UploadCSV_View2(FormView):

	template_name = 'uploadcsv_view2.html'
	assettrans_fields = [{'field':'data_date', 'label':"Date"},
		    {'field':'trans_type', 'label':"Transaction Type"}]
            
	def dispatch(self, request, *args, **kwargs):
		if request.method.lower() in self.http_method_names:
		  handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
		else:
		  handler = self.http_method_not_allowed
		self.request = request
		self.args = args
		self.kwargs = kwargs

		if not self.request.session['assettrans_csvupload_df']:
		  return HttpResponseRedirect(reverse('UploadCSV_view1', 
			  kwargs = {'pk':self.kwargs['pk']}))
		else:
		  choices = gen_choices(self.request.session['assettrans_csvupload_df'].columns)
		  class formset_class(forms.Form):
			assettrans_field = forms.ChoiceField(choices = choices)
		  self.form_class = formset_factory(formset_class, 
			  extra = len(self.assettrans_fields))
		return handler(request, *args, **kwargs)
		
	def post(self, request, *args, **kwargs):
		form_class = self.get_form_class()
		form = self.get_form(form_class)
		if form.is_valid():
		  
		  csv_df = self.request.session['assettrans_csvupload_df']
		  field_map = 
		    [int(field.get('assettrans_field',0)) 
		     for field in form.cleaned_data]

		  assettrans_df = self.process_csv(csv_df, field_map)

		  self.request.session['assettrans_df'] = assettrans_df
		  return HttpResponseRedirect(reverse('UploadCSV_view3', kwargs = {'pk':self.kwargs['pk']}))
		else:
		  return self.form_invalid(form)

class UploadCSV_View3(FormView):

	def post(self, request, *args, **kwargs):
		form_class = self.get_form_class()
		form = self.get_form(form_class)
		if form.is_valid():
		  assettrans_df = self.request.session['assettrans_df']
		  for asset_trans_inst in assettrans_df['asset_trans']:
			asset_trans_inst.save()
		  
		  #Send signal notifying of update to transactions data.
		  update_pah_sig.send(sender=UploadCSV_View3, 
			params_list = self.calc_params_list(assettrans_df))
		  return self.form_valid(form)
		else:
		  return self.form_invalid(form)
