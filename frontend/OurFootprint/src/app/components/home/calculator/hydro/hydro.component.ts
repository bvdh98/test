import { Component, OnInit, ViewChild } from '@angular/core'
import { MatSnackBar } from '@angular/material/snack-bar'
import { UtilitiesService } from 'src/app/services/utilities.service'
import { MatTableDataSource, MatTable } from '@angular/material/table'
import { map } from 'rxjs/operators'

@Component({
  selector: 'app-hydro',
  templateUrl: './hydro.component.html',
  styleUrls: ['./hydro.component.scss'],
})
export class HydroComponent implements OnInit {
  // A reference to the mat table that is a child of this component
  @ViewChild(MatTable) table: MatTable< /* HydroRow */ any>

  // This is referenced in the html and used to define what columns should be displayed.
  readonly displayedColumns: string[] = ['month', 'consumption', 'delete']

  // An object that is essentially a list that holds the data that will be displayed in the table rows
  dataSource = new MatTableDataSource< /* HydroRow */ any>()

  private bill: File

  constructor(private snackBar: MatSnackBar, private utilitiesService: UtilitiesService) { }

  ngOnInit(): void {
    // Load previous rows from that this user entered
    this.utilitiesService.getHydroRows().pipe(
      // make sure an array was returned before calling map on it
      // convert the rows into a format that the ui table can read
      map((rows) => rows.map ? rows.map(row => row) : [])
    ).subscribe((rows) =>
      this.dataSource.data.push(...rows)
    )
  }

  onUploadClicked(fileList) {
    // TODO: Handle this case more gracefully, the upload button shouldn't be available when there is no file to be uploaded
    if (!fileList || !fileList[0]){
      console.error('A file could not be found, was it already uploaded?')
      return
    }

    if (!this.validateFile(fileList[0].name)) {
      this.snackBar.open('Unsupported File Type!', 'Undo', {duration: 3000})
      return
    }

    this.bill = fileList[0]
    // make a request to back end to upload the file
    this.utilitiesService.uploadHydroBill(fileList[0]).then(response => {
        const jsonResponse: Array<JSON> = (response as Array<JSON>)
        console.log('backend returned: ' + JSON.stringify(jsonResponse))
        console.log(jsonResponse)
        for (const row of jsonResponse) {
          this.addRow(row, this.table, this.dataSource)
        }
    })
  }

  // TODO: store this function elsewhere and reference it (duplicated in hydro component)
  validateFile(filename: string): boolean {
    const extension = filename.substring(filename.lastIndexOf('.') + 1)
    return (extension.toLowerCase() === 'csv' ? true : false)
  }

  // TODO: Reuse code
  addRow(row: any, table: MatTable<any>, dataSource: MatTableDataSource<any>): void {
    dataSource.data.push(row)
    this.renderTable(table)
  }

  // TODO: Reuse code
  /**
   * Remove a row from the ui table and the database
   * @param row the row index in the UI table
   * @param table a reference to the able that will need to be re-rendered
   * @param dataSource a reference to the datasource that the row should be removed from (for ui)
   * @param id the id in the database
   */
   deleteRow(row: number, table: MatTable<any>, dataSource: MatTableDataSource<any>, id: number): void {
    // Delete the row from the backed DB
    this.utilitiesService.deleteFortisRow(id).toPromise()

    // delete the row from the UI
    dataSource.data.splice(row, 1) // deletes the row
    this.renderTable(table)
  }

  // TODO: Reuse code
  private renderTable(table: MatTable<any>): void {
    if (table) { // table can be null when it isn't displayed because of *ngIf
      table.renderRows() // The table doesn't re render unless we tell it to. How very non-angular.
    }
  }

}
