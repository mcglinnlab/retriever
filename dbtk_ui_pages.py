"""Classes representing pages for the DBTK wizard.

"""
import wx
import wx.wizard
from dbtk_tools import *

class DbTkWizard(wx.wizard.Wizard):
    def __init__(self, parent, id, title, dbtk_list, engine_list):
        wx.wizard.Wizard.__init__(self, parent, id, title)
        self.page = []
        self.dbtk_list = dbtk_list
        self.engine_list = engine_list
        # Create the wizard pages
        # 0: Title page
        # 1: Choose db
        # 2: Connection info
        # 3: Dataset selection
        # 4: End
        self.page.append(self.TitledPage(self, "Welcome", 
"""Welcome to the Database Toolkit wizard.

This wizard will walk you through the process of downloading
and installing ecological datasets.

This wizard requires that you have one or more of the supported
database systems installed. You must also have either an active
connection to the internet, or the raw data files stored locally 
on your computer.

Supported database systems currently include:\n\n""" + 
", ".join([db.name for db in engine_list])))
        
        self.page.append(self.ChooseDbPage(self, "Select Database", 
                                      "Please select your database platform:\n"))
        
        self.page.append(self.ConnectPage(self, 
                                     "Connection Info", 
                                     "Please enter your connection information: \n"))
        self.page[1].Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING, self.page[2].Draw)
        
        if len(self.dbtk_list) > 1:
            self.page.append(self.DatasetPage(self, "Select Datasets", 
                                    "Check each dataset to be downloaded:\n"))
        
        self.page.append(self.TitledPage(self, "Finished", 
                               "That's it! Click Finish to download and install " +
                               "your data."))
    
        
        for i in range(len(self.page) - 1):
            wx.wizard.WizardPageSimple_Chain(self.page[i], self.page[i + 1])
            
        self.FitToPage(self.page[0])    
    
    
    class TitledPage(wx.wizard.WizardPageSimple):
        """A standard wizard page with a title and label."""
        def __init__(self, parent, title, label):
            wx.wizard.WizardPageSimple.__init__(self, parent)
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self.SetSizer(self.sizer)
            titleText = wx.StaticText(self, -1, title)
            titleText.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.sizer.Add(titleText, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
            self.label = wx.StaticText(self, -1)
            self.sizer.Add(self.label, 0, wx.EXPAND | wx.ALL, 5)
            self.label.Wrap(100)
            if label:
                self.sizer.Add(wx.StaticText(self, -1, label))
                    
    
    class ChooseDbPage(TitledPage):
        def __init__(self, parent, title, label):
            parent.TitledPage.__init__(self, parent, title, label)
            engine_list = parent.engine_list
            
            dblist = wx.ListBox(self, -1, 
                                choices=[db.name for db in engine_list], 
                                style=wx.LB_SINGLE)
            self.dblist = dblist
            self.dblist.SetSelection(0)
            self.sizer.Add(self.dblist,
                              0, wx.EXPAND | wx.ALL, 5)
            self.sizer.Add(wx.StaticText(self, -1, "\n"))
            self.keepdata = wx.CheckBox(self, -1, "Keep raw data files")
            self.keepdata.SetValue(True)    
            self.sizer.Add(self.keepdata)
            self.uselocal = wx.CheckBox(self, -1, 
                                        "Use locally archived files, " +
                                        "if available")
            self.uselocal.SetValue(True)
            self.sizer.Add(self.uselocal)
            self.sizer.Add(wx.StaticText(self, -1, "\n"))
            self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)    
            self.sizer2.Add(wx.StaticText(self, -1, "Data file directory:", 
                                  size=wx.Size(150,35)))
            self.raw_data_dir = wx.TextCtrl(self, -1, 
                                            Engine().RAW_DATA_LOCATION,
                                            size=wx.Size(200,-1))
            self.sizer2.Add(self.raw_data_dir)
            self.dirbtn = wx.Button(self, id=-1, label='Change...',
                                    size=(120, -1))
            self.sizer2.Add(self.dirbtn)
            self.sizer.Add(self.sizer2)                    
            self.dirbtn.Bind(wx.EVT_BUTTON, self.dirbtn_click)
        def dirbtn_click(self, evt):
            dialog = wx.DirDialog(None, message="Choose a directory to " +
                                    "download your data files.")            
            if dialog.ShowModal() == wx.ID_OK:            
               self.raw_data_dir.SetValue(dialog.GetPath())            
            else:
               pass            
            dialog.Destroy()
                        
    
    class ConnectPage(TitledPage):
        """The connection info page."""
        def __init__(self, parent, title, label):
            parent.TitledPage.__init__(self, parent, title, label)
            self.option = dict()
            self.sel = ""
            self.fields = wx.BoxSizer(wx.VERTICAL)
        def Draw(self, evt):
            """When the page is drawn, it may need to update its fields if 
            the selected database has changed."""
            if len(self.Parent.page[1].dblist.GetStringSelection()) == 0 and evt.Direction:
                evt.Veto()                  
            else:
                if self.sel != self.Parent.page[1].dblist.GetStringSelection():
                    self.sel = self.Parent.page[1].dblist.GetStringSelection()
                    self.engine = Engine()
                    for db in self.Parent.engine_list:
                        if db.name == self.sel:
                            self.engine = db
                    self.fields.Clear(True)     
                    self.fields = wx.BoxSizer(wx.VERTICAL)                
                    self.fieldset = dict()
                    self.option = dict()
                    for opt in self.engine.required_opts:
                        self.fieldset[opt[0]] = wx.BoxSizer(wx.HORIZONTAL)
                        label = wx.StaticText(self, -1, opt[0] + ": ", 
                                              size=wx.Size(90,35))
                        if opt[0] == "password":
                            txt = wx.TextCtrl(self, -1, 
                                              str(opt[2]), 
                                              size=wx.Size(200,-1), 
                                              style=wx.TE_PASSWORD)
                        else:
                            txt = wx.TextCtrl(self, -1, str(opt[2]),
                                              size=wx.Size(200,-1))
                        self.option[opt[0]] = txt
                        self.fieldset[opt[0]].AddMany([label, 
                                                       self.option[opt[0]]])
                        if opt[0] == "file":
                            def open_file_dialog(evt):
                                filter = ""
                                if opt[3]:
                                    filter = opt[3] + "|"
                                filter += "All files (*.*)|*.*"                                    
                                dialog = wx.FileDialog(None, style = wx.OPEN,
                                                       wildcard = filter)
                                if dialog.ShowModal() == wx.ID_OK:
                                    self.option[opt[0]].SetValue(dialog.GetPath())
                            self.browse = wx.Button(self, -1, "Choose...")
                            self.fieldset[opt[0]].Add(self.browse)
                            self.browse.Bind(wx.EVT_BUTTON, open_file_dialog)                        
                        self.fieldset[opt[0]].Layout()
                        self.fields.Add(self.fieldset[opt[0]])
                    #self.fields = wx.BoxSizer(wx.VERTICAL)
                    self.fields.Layout()
                    self.sizer.Add(self.fields)
                    self.sizer.Layout()
    
    
    class DatasetPage(TitledPage):
        """The dataset selection page."""
        def __init__(self, parent, title, label):
            parent.TitledPage.__init__(self, parent, title, label)
            dbtk_list = parent.dbtk_list
            # All checkbox
            self.checkallbox = wx.CheckBox(self, -1, "All")
            self.checkallbox.SetValue(True)
            self.sizer.Add(self.checkallbox)            
            self.checkallbox.Bind(wx.EVT_CHECKBOX, self.CheckAll)            
            # CheckListBox of scripts
            scripts = [script.name for script in dbtk_list]
            self.scriptlist = wx.CheckListBox(self, -1, choices=scripts)
            public_scripts = [script.name for script in dbtk_list if script.public]
            self.scriptlist.SetCheckedStrings(public_scripts)
            self.sizer.Add(self.scriptlist)
            # Add dataset button
            self.addbtn = wx.Button(self, -1, "Add...")
            self.sizer.Add(self.addbtn)
            self.addbtn.Bind(wx.EVT_BUTTON, self.AddDataset)            
            # Check that at least one dataset is selected before proceeding
            self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING, self.CheckValues)            
        def AddDataset(self, evt):
            add_dataset = self.Parent.AddDatasetWizard(self.Parent, -1, 'Add Dataset')            
            if add_dataset.RunWizard(add_dataset.page[0]):                
                dataset_url = add_dataset.url.GetValue()
                dbname = add_dataset.dbname.GetValue()
                tablename = add_dataset.tablename.GetValue()
                fullname = dbname
                if tablename:
                    fullname += "." + tablename              
                if dbname and dataset_url:
                    if not (fullname in self.scriptlist.GetItems()):
                        self.Parent.dbtk_list.append(AutoDbTk(fullname,
                                                              dbname,
                                                              tablename, 
                                                              dataset_url))
                        self.scriptlist.Append(fullname)
                        
                    else:
                        wx.MessageBox("You already have a dataset named " + dataset_name + ".")
                    self.scriptlist.SetCheckedStrings(self.scriptlist.GetCheckedStrings() + (fullname,))
            add_dataset.Destroy()
        def CheckAll(self, evt):
            if self.checkallbox.GetValue():
                self.scriptlist.SetCheckedStrings([script.name for script in self.Parent.dbtk_list])
            else:
                self.scriptlist.SetCheckedStrings([])
        def CheckValues(self, evt):  
            """Users can't continue from this page without checking at least
            one dataset."""
            if len(self.scriptlist.GetCheckedStrings()) == 0 and evt.Direction:
                evt.Veto()
            elif evt.Direction:
                checked = self.scriptlist.GetCheckedStrings()
                warn = [script.name for script in self.Parent.dbtk_list 
                        if not script.public and script.name in checked]
                if warn:
                    warning = "Warning: the following datasets are not "
                    warning += "publicly available. You must have the raw "
                    warning += "data files in your data file directory first."
                    warning += "\n\n" + ','.join(warn) + "\n\n"
                    warning += "Do you want to continue?"
                    warndialog = wx.MessageDialog(None, 
                                                  warning, 
                                                  "Warning", 
                                                  style = wx.YES_NO)
                    if warndialog.ShowModal() != wx.ID_YES:
                        evt.Veto()
                        
                         
    class AddDatasetWizard(wx.wizard.Wizard):
        def __init__(self, parent, id, title):
            wx.wizard.Wizard.__init__(self, parent, id, title)            
            
            self.page = []
            self.page.append(parent.TitledPage(self, "Add Dataset", ""))
            
            hbox = wx.FlexGridSizer(rows=3, cols=2)                        
            self.url = wx.TextCtrl(self, -1, "http://",
                                    size=wx.Size(150,-1))
            self.dbname = wx.TextCtrl(self, -1, "",
                                      size=wx.Size(150,-1))
            self.tablename = wx.TextCtrl(self, -1, "",
                                         size=wx.Size(150,-1))
            hbox.AddMany([
                          (wx.StaticText(self, -1, "URL: "),),
                          (self.url,),
                          (wx.StaticText(self, -1, "Database Name: "),),
                          (self.dbname,),
                          (wx.StaticText(self, -1, "Table Name: "),),
                          (self.tablename,)
                          ])
            hbox.Layout()
               
            self.page[0].sizer.Add(hbox)
            self.page[0].sizer.Layout()