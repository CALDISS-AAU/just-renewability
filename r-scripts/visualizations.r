library(ggplot2)
library(readr)
library(readxl)
library(dplyr)
library(writexl)

#ready_table_spain <- "./output/articles_sp_monthly_summary.csv"
#ready_table_argentina <- "./output/articles_arg_monthly_summary.csv"

setwd("/work/CALDISS-projects/Leverancer/dlvr_just-renewability_F24")

ready_table_argentina <- "/work/CALDISS-projects/Leverancer/dlvr_just-renewability_F24/output/articles_arg_monthly_summary.csv"
ready_table_spain <- "/work/CALDISS-projects/Leverancer/dlvr_just-renewability_F24/output/articles_sp_monthly_summary.csv"

keywords_translate <- tribble(
  ~from, ~to,
  "(reindustrialización OR industrialización)", "(Reindustrialisation OR Industrialisation)",
  "(hidrógeno rosa OR nuclear)", "(Pink hydrogen OR Nuclear)",
  "agua", "Water",
  "apoyo", "Support", 
  "audiencias públicas", "Public hearings",
  "ciudadano", "Citizen",
  "crecimiento", "Growth", 
  "energía renovable", "Renewable energy",
  "eólica", "Wind",
  "futuro", "Future",
  "hidrógeno verde", "Green hydrogen",
  "impacto medioambiental", "Environmental impact", 
  "participación", "Participation",
  "solar", "Solar"
)
keywords_translate <- mutate(keywords_translate, from = factor(from, levels=from), to = factor(to, levels=to))

# X-axis: Year-Month and Y-axis: number of articles
visualize <- function(input_dataset, output_png, title) {
  figure <- read_csv(input_dataset, show_col_types = FALSE)
  figure <- figure[order(figure[["Year-Month"]]), ]  #Year and month must be ordered
  figure[["Year-Month"]] <- factor(
    figure[["Year-Month"]],
    levels = unique(figure[["Year-Month"]])
  )

  plot <- ggplot(figure, aes(x = `Year-Month`)) +    
    #Step 3: get rid of "USED" and rename total to base. 
    geom_col(
      aes(y = N_articles_total, fill = "Base"),
      width = 0.9
    ) +
    geom_col(
      aes(y = N_articles_filtered, fill = "Filtered"),
      width = 0.9
    ) +
    #geom_col(
    #  aes(y = N_articles_used, fill = "Used"),
    #  width = 0.9
    #) +

    #Step4: please add percentage onto the bar icons
    geom_text(
      aes(
        y= N_articles_filtered,
        label= paste0(round(N_articles_filtered/N_articles_total * 100), "%")
        ),
      colour = "white",
      nudge_y = -100
    ) +
    scale_fill_manual(
      values = c(
        "Base" = "darkblue",
        "Filtered" = "royalblue",
        "Used" = "lightblue"
      ),
      breaks = c("Base", "Filtered", "Used"),
      name = NULL
    ) +
    scale_y_continuous(limits = c(0, 3000), breaks = c(0, 500, 1000, 1500, 2000, 2500, 3000)) + 
    labs(
      x = "Year-Month",
      y = "Number of articles",
      title = title
    ) +
    theme_minimal(base_size = 14) + 
    theme(
      #panel.background = element_rect(fill = "#EAEAF2", color = NA),
      #plot.background = element_rect(fill = "white", color = NA),
      panel.grid.major = element_line(color = "white", linewidth = 0.7),
      panel.grid.minor = element_line(color = "white", linewidth = 0.35),
      axis.text.x = element_text(angle = 0, vjust = 0.5, hjust = 0.5)
    )

  ggsave(output_png, plot = plot, width = 11, height = 9, dpi=300, units = "in", scale=1)
}

visualize(
  ready_table_spain,
  "./output/plots/articles_sp_timeline.png",
  "Spain articles chronological order"
)
visualize(
  ready_table_argentina,
  "./output/plots/articles_arg_timeline.png",
  "Argentina articles chronological order"
)


# HEATMAPS
keyword_overlap_spain_input <-
  "./output/article-filtering/articles_sp_meta_2024-08-22_renewable-energy_green-hydrogen_selection-nov24.xlsx"
keyword_overlap_argentina_input <-
  "./output/article-filtering/articles_arg_meta_2024-08-22_renewable-energy_green-hydrogen_revisadoLW_jun25.xlsx"

prepare_keyword_data <- function(input_excel) {
  article_data <- read_excel(input_excel)
  keyword_columns <- grep("^keyword_", names(article_data), value = TRUE)

  other_keyword_columns <- setdiff(keyword_columns, c("keyword_conflicto", "keyword_power to x"))  #Step1 : get rid of "keyword_power to x". c = combine
  
  keyword_data <- article_data |> 
    select(all_of(other_keyword_columns))

  any_keyword_match <- rowSums(keyword_data, na.rm = TRUE) > 0

  keyword_data <- keyword_data[any_keyword_match, ]

  return(keyword_data)
}


#Step2: Create frequency tables for keywords. Count no text matched per keywrds

keyword_frequency_table <- function(input_excel, output_path){
  article_data <- read_excel(input_excel)

  keyword_columns <- setdiff(
    #find column name starting with keyword_
    grep("^keyword_", names(article_data), value= TRUE),
    c("keyword_conflicto", "keyword_power to x")
  )

  #add each col vertically and save the number in total_text
  frequency_table <- data.frame(
    keyword = sub ("^keyword_", "", keyword_columns),
    total_text = colSums(article_data[keyword_columns], na.rm = TRUE) 
  )

  frequency_table$percent_of_total_text <- round(frequency_table$total_text / nrow(article_data) * 100,
  1)

  write_xlsx(frequency_table, output_path)
}

#Run for SP + ARG

keyword_frequency_table(keyword_overlap_spain_input, "./output/tables/keyword_frequency_spain.xlsx")
keyword_frequency_table(keyword_overlap_argentina_input, "./output/tables/keyword_frequency_argentina.xlsx")



compute_keyword_overlap <- function(keyword_data) {
  keyword_matrix <- as.matrix(keyword_data)
  storage.mode(keyword_matrix) <- "numeric"

  co_occurrence_counts <- crossprod(keyword_matrix)
  keyword_totals <- colSums(keyword_matrix)

  overlap_matrix <- sweep(co_occurrence_counts, 1, keyword_totals, "/")
  overlap_matrix[keyword_totals == 0, ] <- NA_real_
  
  return(overlap_matrix)
}

plot_keyword_overlap_heatmap <- function(input_excel, output_png, title_use) {
  filtered_keyword_data <- prepare_keyword_data(input_excel)
  overlap_matrix <- compute_keyword_overlap(filtered_keyword_data)
  keyword_labels <- sub("^keyword_", "", colnames(overlap_matrix))

  plot_data <- as.data.frame(as.table(overlap_matrix), stringsAsFactors = FALSE)
  names(plot_data) <- c("keyword_a", "keyword_b", "proportion")

  plot_data$keyword_a <- factor(
    sub("^keyword_", "", plot_data$keyword_a),
    levels = keyword_labels
  )
  plot_data$keyword_b <- factor(
    sub("^keyword_", "", plot_data$keyword_b),
    levels = keyword_labels
  )
  plot_data$label <- ifelse(
    is.na(plot_data$proportion),
    "",
    paste0(round(plot_data$proportion * 100), "%")
  )
  plot_data$text_color <- ifelse(
    is.na(plot_data$proportion),
    "black",
    ifelse(plot_data$proportion >= 0.5, "white", "black")
  )

  plot_data <- plot_data |> 
    mutate(
      label = if_else(keyword_a == keyword_b, "-", label)
    )
  
  # translate
  plot_data <- mutate(plot_data,
                      keyword_a = recode_values(keyword_a, from = keywords_translate$from, to = keywords_translate$to),
                      keyword_b = recode_values(keyword_b, from = keywords_translate$from, to = keywords_translate$to)
  )

  heatmap_plot <- ggplot(plot_data, aes(x = keyword_b, y = keyword_a, fill = proportion)) +
    geom_tile(color = "white", linewidth = 0.4) +
    geom_text(
      aes(label = label, color = text_color),
      size = 3
    ) +  
    annotate(
      "rect",
      xmin = 0,   # extend left beyond first tile
      xmax = length(unique(plot_data$keyword_b)) + 1,
      ymin = 11 - 0.5,
      ymax = 11 + 0.5,
      fill = NA,
      colour = "darkred",
      linewidth = 1
    ) +
    scale_fill_gradient(
      low = "#F7FBFF",
      high = "#08306B",
      limits = c(0, 1),
      na.value = "grey90",
      labels = function(values) paste0(round(values * 100), "%"),
      name = "Overlap"
    ) +
    scale_colour_identity() + 
    labs(
      x = "Article also mentioning [keyword]",
      y =  "Articles about [keyword]",
      title = get("title_use", envir=environment())
    ) +
    coord_fixed() +
    theme_minimal(base_size = 14) +
    theme(
      panel.grid = element_blank(),
      axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1),
      axis.title = element_text(face = "bold")
    )

  dir.create(dirname(output_png), recursive = TRUE, showWarnings = FALSE)
  ggsave(output_png, plot = heatmap_plot, width = 11, height = 9, dpi=300, units = "in", scale=1)
  
  return(heatmap_plot)
}

plot_keyword_overlap_heatmap(
  keyword_overlap_spain_input,
  "./output/plots/keyword_overlap_sp.png",
  "Spain Keyword Overlap"
)

plot_keyword_overlap_heatmap(
  keyword_overlap_argentina_input,
  "./output/plots/keyword_overlap_arg.png",
  "Argentina Keyword Overlap"
)





